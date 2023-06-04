import json
import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from snippets.models import Snippet, SnippetFavorite


@pytest.mark.django_db
class TestSnippetListAPIView:
    url = reverse("snippet-list")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
        )
        self.user2 = initial_users["user2"]

    def test_user_snippet(self, client):
        """
        User can see his own snippets
        """
        snippet_count = Snippet.objects.count()
        Snippet.objects.create(user=self.user1, title="Python snippet")

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == snippet_count + 1

    def test_foreign_snippet(self, client):
        """
        User cannot see snippets of other users
        """
        snippet_count = Snippet.objects.count()
        Snippet.objects.create(user=self.user2, title="Python snippet")

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == snippet_count

    def test_no_permission(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 403

    def test_favorite_filter(self, client):
        snippet1 = Snippet.objects.create(user=self.user1, title="Snippet 1")
        Snippet.objects.create(user=self.user1, title="Snippet 2")
        Snippet.objects.create(user=self.user1, title="Snippet 3")
        Snippet.objects.create(user=self.user1, title="Snippet 4")

        SnippetFavorite.objects.create(user=self.user1, snippet=snippet1)

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4

        response = client.get(self.url + "?favorite=true")
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

        response = client.get(self.url + "?favorite=false")
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 3


@pytest.mark.django_db
class TestSnippetListAPICreate:
    url = reverse("snippet-list")
    create_data = {
        "title": "Python snippet",
        "description": "",
        "team": "",
    }

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="add_snippet"),
        )
        self.user2 = initial_users["user2"]

    def assert_create_response(self, response):
        assert response.status_code == 201
        assert response.data["user"] == self.user1.pk
        assert response.data["title"] == self.create_data["title"]
        assert response.data["description"] == self.create_data["description"]
        assert response.data["visibility"] == Snippet.VISIBILITY_PRIVATE
        assert response.data["team"] is None
        assert response.data["user_display"] == self.user1.username
        assert response.data["files"] == []
        assert response.data["labels"] == []
        assert response.data["favorite"] is False

    def test_user_snippet(self, client):
        """
        User should be able to create a new snippet as he received the required permissions.
        Logged in user will be assigned automatically
        """
        response = client.post(self.url, self.create_data)
        self.assert_create_response(response)

    def test_minimum_fields(self, client):
        """
        Create a new snippet by sending minimal fields in payload
        """
        data = {}
        response = client.post(self.url, data)
        assert response.status_code == 400

        data["title"] = self.create_data["title"]
        response = client.post(self.url, data)
        self.assert_create_response(response)

    def test_foreign_user_snippet(self, client):
        """
        User should be able to create a new snippet as he received the required permissions.
        Logged in user will be assigned automatically
        :return:
        """
        create_data = self.create_data.copy()
        create_data.update({"user": self.user2.pk})

        response = client.post(self.url, create_data)
        self.assert_create_response(response)

    def test_no_permission(self, client, auth_user2):
        response = client.post(self.url, self.create_data)
        assert response.status_code == 403


@pytest.fixture
def snippet_detail_setup(initial_users):
    user1 = initial_users["user1"]
    snippet = Snippet.objects.create(user=user1, title="Python snippet")
    url = reverse("snippet-detail", kwargs={"pk": snippet.pk})
    snippet_count = Snippet.objects.count()

    return {
        "url": url,
        "snippet": snippet,
        "snippet_count": snippet_count,
    }


@pytest.mark.django_db
class TestSnippetDetailAPIView:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, snippet_detail_setup):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
        )
        self.user2 = initial_users["user2"]
        self.url = snippet_detail_setup["url"]
        self.snippet = snippet_detail_setup["snippet"]
        self.snippet_count = snippet_detail_setup["snippet_count"]

    def test_user_snippet(self, client):
        """
        User should see snippets that are assigned to him
        """
        response = client.get(self.url)
        assert response.status_code == 200
        assert Snippet.objects.count() == self.snippet_count

        assert response.data["title"] == self.snippet.title
        assert response.data["user"] == self.user1.pk
        assert response.data["description"] == self.snippet.description
        assert response.data["visibility"] == Snippet.VISIBILITY_PRIVATE
        assert response.data["team"] is None
        assert response.data["user_display"] == self.user1.username
        assert response.data["files"] == []
        assert response.data["labels"] == []
        assert response.data["favorite"] is False

    def test_foreign_user_snippet(self, client):
        """
        User should not see snippets that are not assigned to him
        """
        self.snippet.user = self.user2
        self.snippet.save()

        response = client.get(self.url)
        assert response.status_code == 404
        assert Snippet.objects.count() == self.snippet_count

    def test_no_permission(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 404
        assert Snippet.objects.count() == self.snippet_count


@pytest.mark.django_db
class TestSnippetDetailAPIUpdate:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, snippet_detail_setup):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="change_snippet"),
        )
        self.user2 = initial_users["user2"]
        self.url = snippet_detail_setup["url"]
        self.snippet = snippet_detail_setup["snippet"]
        self.snippet_count = snippet_detail_setup["snippet_count"]

    def test_user_snippet(self, client):
        response = client.put(
            self.url,
            {
                "title": "Python snippet update 1",
                "description": "Update description",
            },
        )
        assert response.status_code == 200
        assert Snippet.objects.count() == self.snippet_count

        assert response.data["title"] == "Python snippet update 1"
        assert response.data["user"] == self.user1.pk
        assert response.data["description"] == "Update description"
        assert response.data["visibility"] == Snippet.VISIBILITY_PRIVATE
        assert response.data["team"] is None
        assert response.data["user_display"] == self.user1.username
        assert response.data["files"] == []
        assert response.data["labels"] == []
        assert response.data["favorite"] is False

        response = client.put(
            self.url,
            {
                "description": "Update description only",
            },
        )
        assert response.status_code == 400
        assert Snippet.objects.count() == self.snippet_count

        response = client.patch(
            self.url,
            {
                "description": "Update description only",
            },
        )
        assert response.status_code == 200
        assert Snippet.objects.count() == self.snippet_count

        assert response.data["title"] == "Python snippet update 1"
        assert response.data["user"] == self.user1.pk
        assert response.data["description"] == "Update description only"
        assert response.data["visibility"] == Snippet.VISIBILITY_PRIVATE
        assert response.data["team"] is None
        assert response.data["user_display"] == self.user1.username
        assert response.data["files"] == []
        assert response.data["labels"] == []
        assert response.data["favorite"] is False

    def test_foreign_user_snippet(self, client):
        self.snippet.user = self.user2
        self.snippet.save()

        response = client.put(
            self.url,
            {
                "title": "Python snippet update 1",
                "description": "Update description",
            },
        )
        assert response.status_code == 404
        assert Snippet.objects.count() == self.snippet_count

        response = client.patch(
            self.url,
            {
                "description": "Update description only",
            },
        )
        assert response.status_code == 404
        assert Snippet.objects.count() == self.snippet_count

    def test_no_permission(self, client, auth_user2):
        response = client.put(self.url, {})
        assert response.status_code == 403
        assert Snippet.objects.count() == self.snippet_count

        response = client.patch(self.url, {})
        assert response.status_code == 403
        assert Snippet.objects.count() == self.snippet_count


@pytest.mark.django_db
class TestSnippetDetailAPIDelete:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, snippet_detail_setup):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="delete_snippet"),
        )
        self.user2 = initial_users["user2"]
        self.url = snippet_detail_setup["url"]
        self.snippet = snippet_detail_setup["snippet"]
        self.snippet_count = snippet_detail_setup["snippet_count"]

    def test_user_snippet(self, client):
        response = client.delete(self.url)
        assert response.status_code == 204
        assert Snippet.objects.count() == self.snippet_count - 1

    def test_foreign_user_snippet(self, client):
        self.snippet.user = self.user2
        self.snippet.save()

        response = client.delete(self.url)
        assert response.status_code == 404
        assert Snippet.objects.count() == self.snippet_count

    def test_no_permission(self, client, auth_user2):
        response = client.delete(self.url)
        assert response.status_code == 403
        assert Snippet.objects.count() == self.snippet_count
