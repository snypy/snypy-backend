import json

from django.contrib.auth.models import Permission
from django.urls import reverse

from core.tests import BaseAPITestCase
from snippets.models import Snippet, SnippetFavorite


class SnippetListAPIViewTestCase(BaseAPITestCase):
    url = reverse("snippet-list")

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
        )

    def test_user_snippet(self):
        """
        User can see his own snippets
        """
        snippet_count = Snippet.objects.count()
        Snippet.objects.create(user=self.user1, title="Python snippet")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), snippet_count + 1)

    def test_foreign_snippet(self):
        """
        User cannot see snippets of other users
        """
        snippet_count = Snippet.objects.count()
        Snippet.objects.create(user=self.user2, title="Python snippet")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), snippet_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_favorite_filter(self):
        snippet1 = Snippet.objects.create(user=self.user1, title="Snippet 1")
        Snippet.objects.create(user=self.user1, title="Snippet 2")
        Snippet.objects.create(user=self.user1, title="Snippet 3")
        Snippet.objects.create(user=self.user1, title="Snippet 4")

        SnippetFavorite.objects.create(user=self.user1, snippet=snippet1)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 4)

        response = self.client.get(self.url + "?favorite=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 1)

        response = self.client.get(self.url + "?favorite=false")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 3)


class SnippetListAPICreateTestCase(BaseAPITestCase):
    url = reverse("snippet-list")
    create_data = {
        "title": "Python snippet",
        "description": "",
        "team": "",
    }

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="add_snippet"),
        )

    def assert_create_response(self, response):
        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.data["user"], self.user1.pk)
        self.assertEqual(response.data["title"], self.create_data["title"])
        self.assertEqual(response.data["description"], self.create_data["description"])
        self.assertEqual(response.data["visibility"], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data["team"], None)
        self.assertEqual(response.data["user_display"], self.user1.username)
        self.assertListEqual(response.data["files"], [])
        self.assertListEqual(response.data["labels"], [])

    def test_user_snippet(self):
        """
        User should be able to create a new snippet as he received the required permissions.
        Logged in user will be assigned automatically
        """
        response = self.client.post(self.url, self.create_data)
        self.assert_create_response(response)

    def test_minimum_fields(self):
        """
        Create a new snippet by sending minimal fields in payload
        """
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

        data["title"] = self.create_data["title"]
        response = self.client.post(self.url, data)
        self.assert_create_response(response)

    def test_foreign_user_snippet(self):
        """
        User should be able to create a new snippet as he received the required permissions.
        Logged in user will be assigned automatically
        :return:
        """
        create_data = self.create_data.copy()
        create_data.update({"user": self.user2.pk})

        response = self.client.post(self.url, create_data)
        self.assert_create_response(response)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.post(self.url, self.create_data)
        self.assertEqual(response.status_code, 403)


class SnippetDetailAPIVBaseTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.snippet = Snippet.objects.create(user=self.user1, title="Python snippet")
        self.url = reverse("snippet-detail", kwargs={"pk": self.snippet.pk})
        self.snippet_count = Snippet.objects.count()


class SnippetDetailAPIViewTestCase(SnippetDetailAPIVBaseTestCase):
    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
        )

    def test_user_snippet(self):
        """
        User should see snippets that are assigned to him
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

        self.assertEqual(response.data["title"], "Python snippet")
        self.assertEqual(response.data["user"], self.user1.pk)
        self.assertEqual(response.data["description"], "")
        self.assertEqual(response.data["visibility"], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data["team"], None)
        self.assertEqual(response.data["user_display"], self.user1.username)
        self.assertListEqual(response.data["files"], [])
        self.assertListEqual(response.data["labels"], [])

    def test_foreign_user_snippet(self):
        """
        User should not see snippets that are not assigned to him
        """
        self.snippet.user = self.user2
        self.snippet.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)


class SnippetDetailAPIUpdateTestCase(SnippetDetailAPIVBaseTestCase):
    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename="change_snippet"),
        )

    def test_user_snippet(self):
        response = self.client.put(
            self.url,
            {
                "title": "Python snippet update 1",
                "description": "Update description",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

        self.assertEqual(response.data["title"], "Python snippet update 1")
        self.assertEqual(response.data["user"], self.user1.pk)
        self.assertEqual(response.data["description"], "Update description")
        self.assertEqual(response.data["visibility"], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data["team"], None)
        self.assertEqual(response.data["user_display"], self.user1.username)
        self.assertListEqual(response.data["files"], [])
        self.assertListEqual(response.data["labels"], [])

        response = self.client.put(
            self.url,
            {
                "description": "Update description only",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

        response = self.client.patch(
            self.url,
            {
                "description": "Update description only",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

        self.assertEqual(response.data["title"], "Python snippet update 1")
        self.assertEqual(response.data["user"], self.user1.pk)
        self.assertEqual(response.data["description"], "Update description only")
        self.assertEqual(response.data["visibility"], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data["team"], None)
        self.assertEqual(response.data["user_display"], self.user1.username)
        self.assertListEqual(response.data["files"], [])
        self.assertListEqual(response.data["labels"], [])

    def test_foreign_user_snippet(self):
        self.snippet.user = self.user2
        self.snippet.save()

        response = self.client.put(
            self.url,
            {
                "title": "Python snippet update 1",
                "description": "Update description",
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

        response = self.client.patch(
            self.url,
            {
                "description": "Update description only",
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)

        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

        response = self.client.patch(self.url, {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)


class SnippetDetailAPIDeleteTestCase(SnippetDetailAPIVBaseTestCase):
    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename="delete_snippet"),
        )

    def test_user_snippet(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Snippet.objects.count(), self.snippet_count - 1)

    def test_foreign_user_snippet(self):
        self.snippet.user = self.user2
        self.snippet.save()

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Snippet.objects.count(), self.snippet_count)
