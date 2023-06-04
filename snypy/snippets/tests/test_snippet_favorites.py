import json
import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from snippets.models import Snippet, SnippetFavorite


@pytest.mark.django_db
class TestSnippetFavoriteListAPIView:
    url = reverse("snippetfavorite-list")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippetfavorite"),
        )

    def test_user_snippet_favorite(self, client):
        """
        User can see his own snippet favorites
        """
        snippet_count = Snippet.objects.count()
        snippet = Snippet.objects.create(user=self.user1, title="Python snippet")
        SnippetFavorite.objects.create(user=self.user1, snippet=snippet)

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == snippet_count + 1

    def test_foreign_snippet_favorite(self, client):
        """
        User cannot see snippet favorites of other users
        """
        snippet_count = Snippet.objects.count()
        snippet = Snippet.objects.create(user=self.user2, title="Python snippet")
        SnippetFavorite.objects.create(user=self.user2, snippet=snippet)

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == snippet_count

    def test_no_permission(self, client, auth_user2):
        """
        User cannot see snippet favorites if he does not have the required permissions
        """
        response = client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestSnippetFavoriteListAPICreate:
    url = reverse("snippetfavorite-list")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.snippet1 = Snippet.objects.create(user=self.user1, title="Snippet user 1")
        self.snippet2 = Snippet.objects.create(user=self.user2, title="Snippet user 2")

        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
            Permission.objects.get(codename="add_snippetfavorite"),
        )

    def test_user_snippet_favorite(self, client):
        """
        User should be able to create a new snippet favorites as he received the required permissions.
        Logged in user will be assigned automatically
        """
        response = client.post(
            self.url,
            {
                "snippet": self.snippet1.pk,
            },
        )
        assert response.status_code == 201
        assert response.data["snippet"] == self.snippet1.pk

        # Test duplicate
        response = client.post(
            self.url,
            {
                "snippet": self.snippet1.pk,
            },
        )
        assert response.status_code == 400

    def test_foreign_user_snippet(self, client):
        """
        User should not be able to create favorites on snippets of other users
        """
        response = client.post(
            self.url,
            {
                "snippet": self.snippet2.pk,
            },
        )
        assert response.status_code == 400

    def test_no_permission(self, client, auth_user2):
        response = client.post(
            self.url,
            {
                "snippet": self.snippet1.pk,
            },
        )
        assert response.status_code == 403


@pytest.fixture
def snippet_favorite_detail_setup(initial_users):
    snippet = Snippet.objects.create(user=initial_users["user1"], title="Python snippet")
    snippet_favorite = SnippetFavorite.objects.create(user=initial_users["user1"], snippet=snippet)
    url = reverse("snippetfavorite-detail", kwargs={"pk": snippet.pk})
    snippet_favorite_count = Snippet.objects.count()

    return {
        "url": url,
        "snippet": snippet,
        "snippet_favorite": snippet_favorite,
        "snippet_favorite_count": snippet_favorite_count,
    }


@pytest.mark.django_db
class TestSnippetFavoriteDetailAPIView:
    @pytest.fixture(autouse=True)
    def _setup(self, snippet_favorite_detail_setup, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippetfavorite"),
        )
        self.user2 = initial_users["user2"]
        self.url = snippet_favorite_detail_setup["url"]
        self.snippet = snippet_favorite_detail_setup["snippet"]
        self.snippet_favorite = snippet_favorite_detail_setup["snippet_favorite"]
        self.snippet_favorite_count = snippet_favorite_detail_setup["snippet_favorite_count"]

    def test_user_snippet_favorite(self, client):
        """
        User should see snippet favorites that are assigned to him
        """
        response = client.get(self.url)
        assert response.status_code == 200
        assert response.data["snippet"] == self.snippet.pk
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count

    def test_foreign_user_snippet_favorite(self, client):
        """
        User should not see snippet favorites that are not assigned to him
        """
        self.snippet_favorite.user = self.user2
        self.snippet_favorite.save()

        response = client.get(self.url)
        assert response.status_code == 404
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count

    def test_no_permission(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 403
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count


@pytest.mark.django_db
class TestSnippetFavoriteDetailAPIUpdate:
    @pytest.fixture(autouse=True)
    def _setup(self, snippet_favorite_detail_setup, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="change_snippetfavorite"),
        )
        self.user2 = initial_users["user2"]
        self.url = snippet_favorite_detail_setup["url"]
        self.snippet = snippet_favorite_detail_setup["snippet"]
        self.snippet_favorite = snippet_favorite_detail_setup["snippet_favorite"]
        self.snippet_favorite_count = snippet_favorite_detail_setup["snippet_favorite_count"]

    def test_user_snippet_fvorite(self, client):
        """
        Update own snippet favorites is not allowed
        """
        response = client.put(
            self.url,
            {
                "snippet": self.snippet.pk,
            },
        )
        assert response.status_code == 403
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count

    def test_foreign_user_snippet_favorite(self, client):
        """
        Update foreign snippet favorites is not allowed
        """
        self.snippet_favorite.user = self.user2
        self.snippet_favorite.save()

        response = client.put(
            self.url,
            {
                "snippet": self.snippet.pk,
            },
        )
        assert response.status_code == 404
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count

    def test_no_permission(self, client, auth_user2):
        response = client.put(self.url, {})
        assert response.status_code == 403
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count

        response = client.patch(self.url, {})
        assert response.status_code == 403
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count


@pytest.mark.django_db
class TestSnippetFavoriteDetailAPIDelete:
    @pytest.fixture(autouse=True)
    def _setup(self, snippet_favorite_detail_setup, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippetfavorite"),
            Permission.objects.get(codename="delete_snippetfavorite"),
        )
        self.user2 = initial_users["user2"]
        self.url = snippet_favorite_detail_setup["url"]
        self.snippet = snippet_favorite_detail_setup["snippet"]
        self.snippet_favorite = snippet_favorite_detail_setup["snippet_favorite"]
        self.snippet_favorite_count = snippet_favorite_detail_setup["snippet_favorite_count"]

    def test_user_snippet_favorite(self, client):
        response = client.delete(self.url)
        assert response.status_code == 204
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count - 1

    def test_foreign_user_snippet_favorite(self, client):
        self.snippet_favorite.user = self.user2
        self.snippet_favorite.save()

        response = client.delete(self.url)
        assert response.status_code == 404
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count

    def test_no_permission(self, client, auth_user2):
        response = client.delete(self.url)
        assert response.status_code == 403
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count


@pytest.mark.django_db
class TestSnippetFavoriteToggleAPIVBase:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.token1 = initial_users["token1"]
        self.token2 = initial_users["token2"]

        self.snippet1 = Snippet.objects.create(
            user=self.user1, title="Snippet 1, User 1", visibility=Snippet.VISIBILITY_PRIVATE
        )
        self.snippet2 = Snippet.objects.create(
            user=self.user1, title="Snippet 2, User 1", visibility=Snippet.VISIBILITY_PRIVATE
        )
        self.snippet3 = Snippet.objects.create(
            user=self.user2, title="Snippet 1, User 2", visibility=Snippet.VISIBILITY_PRIVATE
        )
        self.snippet4 = Snippet.objects.create(
            user=self.user2, title="Snippet 2, User 2", visibility=Snippet.VISIBILITY_PUBLIC
        )

        self.snippet1_favorite_url = reverse("snippet-favorite", kwargs={"pk": self.snippet1.pk})
        self.snippet2_favorite_url = reverse("snippet-favorite", kwargs={"pk": self.snippet2.pk})
        self.snippet3_favorite_url = reverse("snippet-favorite", kwargs={"pk": self.snippet3.pk})
        self.snippet4_favorite_url = reverse("snippet-favorite", kwargs={"pk": self.snippet4.pk})

        self.snippet_favorite1 = SnippetFavorite.objects.create(user=self.user1, snippet=self.snippet1)
        self.snippet_favorite3 = SnippetFavorite.objects.create(user=self.user2, snippet=self.snippet3)
        self.snippet_favorite4 = SnippetFavorite.objects.create(user=self.user2, snippet=self.snippet4)
        self.snippet_favorite_count = SnippetFavorite.objects.count()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
            Permission.objects.get(codename="add_snippet"),
        )
        self.user2.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
            Permission.objects.get(codename="add_snippet"),
        )

    def test_remove_own_snippet_favorite(self, client):
        """
        Allows to remove own snippet favorite
        """
        response = client.post(self.snippet1_favorite_url)
        assert response.status_code == 204
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count - 1
        assert response.data is None

    def test_add_snippet_own_favorite(self, client):
        """
        Allows to add own snippet favorite
        """
        response = client.post(self.snippet2_favorite_url)
        assert response.status_code == 201
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count + 1

    def test_add_remove_foreign_private_snippet_favorite(self, client):
        """
        Deny adding and removing foreign private snippet favorites
        """
        response = client.post(self.snippet3_favorite_url)
        assert response.status_code == 404
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count

        # Login as user2
        client.credentials(HTTP_AUTHORIZATION="Token " + self.token2.key)

        response = client.post(self.snippet3_favorite_url)
        assert response.status_code == 204
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count - 1
        assert response.data is None

        response = client.post(self.snippet3_favorite_url)
        assert response.status_code == 201
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count

    def test_add_remove_foreign_public_snippet_favorite(self, client):
        """
        Allow adding and removing foreign public snippet favorites
        """
        response = client.post(self.snippet4_favorite_url)
        assert response.status_code == 201
        assert SnippetFavorite.objects.count() == self.snippet_favorite_count + 1
