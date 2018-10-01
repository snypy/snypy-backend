import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from django_rest_multitokenauth.models import MultiToken
from rest_framework.test import APITestCase

from snippets.models import Snippet

User = get_user_model()


class BaseAPIViewTestCase(APITestCase):

    def setUp(self):
        self.password = "you_cannot_read_this"
        self.user1 = User.objects.create_user("user1", "user1@test.com", self.password)
        self.user2 = User.objects.create_user("user2", "user2@test.com", self.password)
        self.user3 = User.objects.create_user("user3", "user3@test.com", self.password)

        self.token1 = MultiToken.objects.create(user=self.user1)
        self.token2 = MultiToken.objects.create(user=self.user2)

        self.api_authentication(self.token1)

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class SnippetListAPIViewTestCase(BaseAPIViewTestCase):

    url = reverse("snippet-list")

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename='view_snippet'),
        )

    def test_user_snippet(self):
        """
        User should see snippets that are assigned to him
        """
        snippet_count = Snippet.objects.count()
        Snippet.objects.create(user=self.user1, title="Python snippet")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(json.loads(response.content)) == snippet_count + 1)

    def test_foreign_user_snippet(self):
        """
        User should not see snippets that are not assigned to him
        """
        snippet_count = Snippet.objects.count()
        Snippet.objects.create(user=self.user2, title="Python snippet")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(json.loads(response.content)) == snippet_count)


class SnippetListAPICreateTestCase(BaseAPIViewTestCase):

    url = reverse("snippet-list")
    create_data = {
        "title": "Python snippet",
        "description": "",
        "team": "",
    }

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename='add_snippet'),
        )

    def assert_create_response(self, response):
        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.data['user'], self.user1.pk)
        self.assertEqual(response.data['title'], self.create_data['title'])
        self.assertEqual(response.data['description'], self.create_data['description'])
        self.assertEqual(response.data['visibility'], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data['team'], None)
        self.assertEqual(response.data['user_display'], self.user1.username)
        self.assertListEqual(response.data['files'], [])
        self.assertListEqual(response.data['labels'], [])

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

        data['title'] = self.create_data['title']
        response = self.client.post(self.url, data)
        self.assert_create_response(response)

    def test_foreign_user_snippet(self):
        """
        User should be able to create a new snippet as he received the required permissions.
        Logged in user will be assigned automatically
        :return:
        """
        create_data = self.create_data.copy()
        create_data.update({'user': self.user2.pk})

        response = self.client.post(self.url, create_data)
        self.assert_create_response(response)


class SnippetDetailAPIViewTestCase(BaseAPIViewTestCase):

    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename='view_snippet'),
        )

    def test_user_snippet(self):
        """
        User should see snippets that are assigned to him
        """
        snippet = Snippet.objects.create(user=self.user1, title="Python snippet")
        snippet_count = Snippet.objects.count()

        response = self.client.get(reverse("snippet-detail", kwargs={'pk': snippet.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), snippet_count)

        self.assertEqual(response.data['title'], "Python snippet")
        self.assertEqual(response.data['user'], self.user1.pk)
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['visibility'], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data['team'], None)
        self.assertEqual(response.data['user_display'], self.user1.username)
        self.assertListEqual(response.data['files'], [])
        self.assertListEqual(response.data['labels'], [])

    def test_foreign_user_snippet(self):
        """
        User should not see snippets that are not assigned to him
        """
        snippet = Snippet.objects.create(user=self.user2, title="Python snippet")
        snippet_count = Snippet.objects.count()
        response = self.client.get(reverse("snippet-detail", kwargs={'pk': snippet.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), snippet_count)


class SnippetDetailAPIUpdateTestCase(BaseAPIViewTestCase):

    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename='change_snippet'),
        )

    def test_user_snippet(self):
        snippet = Snippet.objects.create(user=self.user1, title="Python snippet")
        snippet_count = Snippet.objects.count()

        response = self.client.put(
            reverse("snippet-detail", kwargs={'pk': snippet.pk}),
            {
                'title': 'Python snippet update 1',
                'description': 'Update description',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), snippet_count)

        self.assertEqual(response.data['title'], "Python snippet update 1")
        self.assertEqual(response.data['user'], self.user1.pk)
        self.assertEqual(response.data['description'], 'Update description')
        self.assertEqual(response.data['visibility'], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data['team'], None)
        self.assertEqual(response.data['user_display'], self.user1.username)
        self.assertListEqual(response.data['files'], [])
        self.assertListEqual(response.data['labels'], [])

        response = self.client.put(
            reverse("snippet-detail", kwargs={'pk': snippet.pk}),
            {
                'description': 'Update description only',
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), snippet_count)

        response = self.client.patch(
            reverse("snippet-detail", kwargs={'pk': snippet.pk}),
            {
                'description': 'Update description only',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), snippet_count)

        self.assertEqual(response.data['title'], "Python snippet update 1")
        self.assertEqual(response.data['user'], self.user1.pk)
        self.assertEqual(response.data['description'], 'Update description only')
        self.assertEqual(response.data['visibility'], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data['team'], None)
        self.assertEqual(response.data['user_display'], self.user1.username)
        self.assertListEqual(response.data['files'], [])
        self.assertListEqual(response.data['labels'], [])
    
    def test_foreign_user_snippet(self):
        snippet = Snippet.objects.create(user=self.user2, title="Python snippet")
        snippet_count = Snippet.objects.count()

        response = self.client.put(
            reverse("snippet-detail", kwargs={'pk': snippet.pk}),
            {
                'title': 'Python snippet update 1',
                'description': 'Update description',
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), snippet_count)
        
        response = self.client.patch(
            reverse("snippet-detail", kwargs={'pk': snippet.pk}),
            {
                'description': 'Update description only',
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), snippet_count)


class SnippetDetailAPIDeleteTestCase(BaseAPIViewTestCase):
    
    def setUp(self):
        super().setUp()
        self.user1.user_permissions.add(
            Permission.objects.get(codename='delete_snippet'),
        )

    def test_user_snippet(self):
        snippet = Snippet.objects.create(user=self.user1, title="Python snippet")
        snippet_count = Snippet.objects.count()

        response = self.client.delete(reverse("snippet-detail", kwargs={'pk': snippet.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Snippet.objects.count(), snippet_count - 1)
    
    def test_foreign_user_snippet(self):
        snippet = Snippet.objects.create(user=self.user2, title="Python snippet")
        snippet_count = Snippet.objects.count()

        response = self.client.delete(reverse("snippet-detail", kwargs={'pk': snippet.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), snippet_count)
