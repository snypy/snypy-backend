import json

from django.contrib.auth.models import Permission
from django.urls import reverse

from core.tests import BaseAPITestCase
from snippets.models import Snippet, SnippetFavorite


class SnippetFavoriteListAPIViewTestCase(BaseAPITestCase):

    url = reverse("snippetfavorite-list")

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippetfavorite"),
        )

    def test_user_snippet_favorite(self):
        """
        User can see his own snippet favorites
        """
        snippet_count = Snippet.objects.count()
        snippet = Snippet.objects.create(user=self.user1, title="Python snippet")
        SnippetFavorite.objects.create(user=self.user1, snippet=snippet)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), snippet_count + 1)

    def test_foreign_snippet_favorite(self):
        """
        User cannot see snippet favorites of other users
        """
        snippet_count = Snippet.objects.count()
        snippet = Snippet.objects.create(user=self.user2, title="Python snippet")
        SnippetFavorite.objects.create(user=self.user2, snippet=snippet)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), snippet_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class SnippetFavoriteListAPICreateTestCase(BaseAPITestCase):

    url = reverse("snippetfavorite-list")

    def setUp(self):
        super().setUp()

        self.snippet1 = Snippet.objects.create(user=self.user1, title="Snippet user 1")
        self.snippet2 = Snippet.objects.create(user=self.user2, title="Snippet user 2")

        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
            Permission.objects.get(codename="add_snippetfavorite"),
        )

    def test_user_snippet_favorite(self):
        """
        User should be able to create a new snippet favorites as he received the required permissions.
        Logged in user will be assigned automatically
        """
        response = self.client.post(
            self.url,
            {
                "snippet": self.snippet1.pk,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["snippet"], self.snippet1.pk)

        # Test duplicate
        response = self.client.post(
            self.url,
            {
                "snippet": self.snippet1.pk,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_foreign_user_snippet(self):
        """
        User should not be able to create favorites on snippets of other users
        """
        response = self.client.post(
            self.url,
            {
                "snippet": self.snippet2.pk,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.post(
            self.url,
            {
                "snippet": self.snippet1.pk,
            },
        )
        self.assertEqual(response.status_code, 403)


class SnippetFavoriteDetailAPIVBaseTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.snippet = Snippet.objects.create(user=self.user1, title="Python snippet")
        self.snippet_favorite = SnippetFavorite.objects.create(user=self.user1, snippet=self.snippet)
        self.url = reverse("snippetfavorite-detail", kwargs={"pk": self.snippet.pk})
        self.snippet_favorite_count = Snippet.objects.count()


class SnippetFavoriteDetailAPIViewTestCase(SnippetFavoriteDetailAPIVBaseTestCase):
    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippetfavorite"),
        )

    def test_user_snippet_favorite(self):
        """
        User should see snippet favorites that are assigned to him
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)
        self.assertEqual(response.data["snippet"], self.snippet.pk)

    def test_foreign_user_snippet_favorite(self):
        """
        User should not see snippet favorites that are not assigned to him
        """
        self.snippet_favorite.user = self.user2
        self.snippet_favorite.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)


class SnippetFavoriteDetailAPIUpdateTestCase(SnippetFavoriteDetailAPIVBaseTestCase):
    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename="change_snippetfavorite"),
        )

    def test_user_snippet_fvorite(self):
        """
        Update own snippet favorites is not allowed
        """
        response = self.client.put(
            self.url,
            {
                "snippet": self.snippet.pk,
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)

    def test_foreign_user_snippet_favorite(self):
        """
        Update foreign snippet favorites is not allowed
        """
        self.snippet_favorite.user = self.user2
        self.snippet_favorite.save()

        response = self.client.put(
            self.url,
            {
                "snippet": self.snippet.pk,
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)

        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)

        response = self.client.patch(self.url, {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)


class SnippetFavoriteDetailAPIDeleteTestCase(SnippetFavoriteDetailAPIVBaseTestCase):
    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippetfavorite"),
            Permission.objects.get(codename="delete_snippetfavorite"),
        )

    def test_user_snippet_favorite(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count - 1)

    def test_foreign_user_snippet_favorite(self):
        self.snippet_favorite.user = self.user2
        self.snippet_favorite.save()

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SnippetFavorite.objects.count(), self.snippet_favorite_count)