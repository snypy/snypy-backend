import json
import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from snippets.models import Snippet
from teams.models import Team, UserTeam


@pytest.fixture
def team_snippet_setup(initial_users):
    url = reverse("snippet-list")

    user1 = initial_users["user1"]
    user2 = initial_users["user2"]

    # Initial Snippets for each user
    Snippet.objects.create(user=user1, title="Python snippet user 1")
    Snippet.objects.create(user=user2, title="Python snippet user 2")

    team1 = Team.objects.create(name="Team 1")
    team2 = Team.objects.create(name="Team 2")
    assert Team.objects.count() == 2

    team1_snippet = Snippet.objects.create(user=user1, title="Python snippet team 1", team=team1)

    team_1_member_count = UserTeam.objects.filter(team=team1).count()
    assert team_1_member_count == 0

    team_2_member_count = UserTeam.objects.filter(team=team2).count()
    assert team_2_member_count == 0

    return {
        "url": url,
        "team1": team1,
        "team2": team2,
        "team1_snippet": team1_snippet,
    }


@pytest.mark.django_db
class TestTeamSnippetListAPIView:
    """
    Snippets can be viewable by their owner and by users that belong to the same team
    that the snippet is assigned to. The visibility of the snippets is not related to the role in the team.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, team_snippet_setup):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="view_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="view_snippet"))

        self.url = team_snippet_setup["url"]
        self.team1 = team_snippet_setup["team1"]
        self.team2 = team_snippet_setup["team2"]
        self.team1_snippet = team_snippet_setup["team1_snippet"]

    def test_team_snippet_owner(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = client.get("%s?team_is_null=True" % self.url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team1.pk))
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team2.pk))
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_team_snippet_other_user_unassigned(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team_is_null=True" % self.url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team1.pk))
        assert response.status_code == 200
        assert len(response.json()) == 0

        response = client.get("%s?team=%d" % (self.url, self.team2.pk))
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_team_snippet_other_user_assigned_as_subscriber(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_SUBSCRIBER)

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = client.get("%s?team_is_null=True" % self.url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team1.pk))
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team2.pk))
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_team_snippet_other_user_assigned_as_contributor(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_CONTRIBUTOR)

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = client.get("%s?team_is_null=True" % self.url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team1.pk))
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team2.pk))
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_team_snippet_other_user_assigned_as_editor(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_EDITOR)

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = client.get("%s?team_is_null=True" % self.url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team1.pk))
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("%s?team=%d" % (self.url, self.team2.pk))
        assert response.status_code == 200
        assert len(response.json()) == 0


@pytest.mark.django_db
class TestTeamSnippetListAPICreate:
    """
    Snippets can be added only on teams the user is assigned when to role is contributor or editor.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, team_snippet_setup):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="add_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="add_snippet"))

        self.url = team_snippet_setup["url"]
        self.team1 = team_snippet_setup["team1"]
        self.team2 = team_snippet_setup["team2"]
        self.team1_snippet = team_snippet_setup["team1_snippet"]

        self.create_data = {
            "title": "Python snippet",
            "description": "",
            "team": self.team1.pk,
        }

    def assert_create_response(self, response):
        assert response.status_code == 201

        assert response.data["user"] == self.user1.pk
        assert response.data["title"] == self.create_data["title"]
        assert response.data["description"] == self.create_data["description"]
        assert response.data["visibility"] == Snippet.VISIBILITY_PRIVATE
        assert response.data["team"] == self.team1.pk
        assert response.data["user_display"] == self.user1.username
        assert response.data["files"] == []
        assert response.data["labels"] == []
        assert response.data["favorite"] is False

    def test_team_snippet_unassigned(self, client):
        response = client.post(self.url, self.create_data)
        assert response.status_code == 400

    def test_team_snippet_other_user_assigned_subscriber(self, client):
        UserTeam.objects.create(team=self.team1, user=self.user1, role=UserTeam.ROLE_SUBSCRIBER)
        response = client.post(self.url, self.create_data)
        assert response.status_code == 400

    def test_team_snippet_other_user_assigned_contributor(self, client):
        UserTeam.objects.create(team=self.team1, user=self.user1, role=UserTeam.ROLE_CONTRIBUTOR)
        response = client.post(self.url, self.create_data)
        self.assert_create_response(response)

    def test_team_snippet_other_user_assigned_editor(self, client):
        UserTeam.objects.create(team=self.team1, user=self.user1, role=UserTeam.ROLE_EDITOR)
        response = client.post(self.url, self.create_data)
        self.assert_create_response(response)


@pytest.mark.django_db
class TestTeamSnippetDetailAPIView:
    """
    Snippets can be viewable by their owner and by users that belong to the same team
    that the snippet is assigned to. The visibility of the snippets is not related to the role in the team.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, team_snippet_setup):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="view_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="view_snippet"))

        self.team1 = team_snippet_setup["team1"]
        self.team2 = team_snippet_setup["team2"]
        self.team1_snippet = team_snippet_setup["team1_snippet"]

        self.url = reverse("snippet-detail", kwargs={"pk": self.team1_snippet.pk})

    def test_team_snippet_owner(self, client):
        response = client.get(self.url)
        assert response.status_code == 200

    def test_team_snippet_other_user_unassigned(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 404

    def test_team_snippet_other_user_assigned_as_subscriber(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_SUBSCRIBER)

        response = client.get(self.url)
        assert response.status_code == 200

    def test_team_snippet_other_user_assigned_as_contributor(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_CONTRIBUTOR)

        response = client.get(self.url)
        assert response.status_code == 200

    def test_team_snippet_other_user_assigned_as_editor(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_EDITOR)

        response = client.get(self.url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestTeamSnippetDetailAPIEdit:
    """
    Snippets can be edited only on teams the user is assigned to with the role editor.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, team_snippet_setup):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="change_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="change_snippet"))

        self.team1 = team_snippet_setup["team1"]
        self.team2 = team_snippet_setup["team2"]
        self.team1_snippet = team_snippet_setup["team1_snippet"]

        self.url = reverse("snippet-detail", kwargs={"pk": self.team1_snippet.pk})
        self.patch_data = {"title": "Python snippet edited"}

    def assert_patch_response(self, response):
        assert response.status_code == 200
        assert response.data["user"] == self.user1.pk
        assert response.data["title"] == self.patch_data["title"]
        assert response.data["description"] == ""
        assert response.data["visibility"] == Snippet.VISIBILITY_PRIVATE
        assert response.data["team"] == self.team1.pk
        assert response.data["user_display"] == self.user1.username
        assert response.data["files"] == []
        assert response.data["labels"] == []
        assert response.data["favorite"] is False

    def test_team_snippet_owner(self, client):
        response = client.patch(self.url, self.patch_data)
        self.assert_patch_response(response)

    def test_team_snippet_other_user_unassigned(self, client, auth_user2):
        response = client.patch(self.url, self.patch_data)
        assert response.status_code == 404

    def test_team_snippet_other_user_assigned_as_subscriber(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_SUBSCRIBER)

        response = client.patch(self.url, self.patch_data)
        assert response.status_code == 403

    def test_team_snippet_other_user_assigned_as_contributor(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_CONTRIBUTOR)

        response = client.patch(self.url, self.patch_data)
        assert response.status_code == 403

    def test_team_snippet_other_user_assigned_as_editor(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_EDITOR)

        response = client.patch(self.url, self.patch_data)
        self.assert_patch_response(response)


@pytest.mark.django_db
class TestTeamSnippetDetailAPIDelete:
    """
    Snippets can be deleted only on teams the user is assigned to with the role editor.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, team_snippet_setup):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="delete_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="delete_snippet"))

        self.team1 = team_snippet_setup["team1"]
        self.team2 = team_snippet_setup["team2"]
        self.team1_snippet = team_snippet_setup["team1_snippet"]

        self.url = reverse("snippet-detail", kwargs={"pk": self.team1_snippet.pk})

    def test_team_snippet_owner(self, client):
        response = client.delete(self.url)
        assert response.status_code == 204

    def test_team_snippet_other_user_unassigned(self, client, auth_user2):
        response = client.delete(self.url)
        assert response.status_code == 404

    def test_team_snippet_other_user_assigned_as_subscriber(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_SUBSCRIBER)

        response = client.delete(self.url)
        assert response.status_code == 403

    def test_team_snippet_other_user_assigned_as_contributor(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_CONTRIBUTOR)

        response = client.delete(self.url)
        assert response.status_code == 403

    def test_team_snippet_other_user_assigned_as_editor(self, client, auth_user2):
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_EDITOR)

        response = client.delete(self.url)
        assert response.status_code == 204
