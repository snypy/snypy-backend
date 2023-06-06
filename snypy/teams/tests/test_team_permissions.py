import json
import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from teams.models import Team, UserTeam


@pytest.mark.django_db
class TestTeamListAPIView:
    url = reverse("team-list")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_team"),
        )

    def test_user_team(self, client):
        """
        User can see teams he is assigned to
        """
        team_count = Team.objects.count()
        team = Team.objects.create(name="Team Python")
        UserTeam.objects.create(user=self.user1, team=team)

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == team_count + 1

    def test_foreign_team(self, client):
        """
        User cannot see teams he is not assigned to
        """
        team_count = Team.objects.count()
        Team.objects.create(name="Team Python")

        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == team_count

    def test_no_permission(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestTeamListAPICreate:
    url = reverse("team-list")
    create_data = {
        "name": "Team Python",
    }

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="add_team"),
        )

    def assert_create_response(self, response):
        assert response.status_code == 201
        assert response.data["name"] == self.create_data["name"]
        assert response.data["users"] == [self.user1.pk]

    def test_user_team(self, client):
        response = client.post(self.url, self.create_data)
        self.assert_create_response(response)

    def test_minimum_fields(self, client):
        """
        Create a new team by sending minimal fields in payload
        """
        data = {}
        response = client.post(self.url, data)
        assert response.status_code == 400

        data["name"] = self.create_data["name"]
        response = client.post(self.url, data)
        self.assert_create_response(response)

    def test_no_permission(self, client, auth_user2):
        response = client.post(self.url, self.create_data)
        assert response.status_code == 403


@pytest.fixture
def team_detail_setup(initial_users):
    user1 = initial_users["user1"]
    team = Team.objects.create(name="Team Python")
    user1_team = UserTeam.objects.create(user=user1, team=team)

    url = reverse("team-detail", kwargs={"pk": team.pk})
    team_count = Team.objects.count()

    return {
        "url": url,
        "team": team,
        "user1_team": user1_team,
        "team_count": team_count,
    }


@pytest.mark.django_db
class TestTeamDetailAPIView:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, team_detail_setup):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_team"),
        )
        self.user2 = initial_users["user2"]
        self.url = team_detail_setup["url"]
        self.team = team_detail_setup["team"]
        self.user1_team = team_detail_setup["user1_team"]
        self.team_count = team_detail_setup["team_count"]

    def test_user_team(self, client):
        """
        User can see teams he is not assigned to
        """
        response = client.get(self.url)
        assert response.status_code == 200
        assert Team.objects.count() == self.team_count
        assert response.data["name"] == "Team Python"
        assert response.data["users"] == [self.user1.pk]

    def test_foreign_team(self, client):
        """
        User cannot see teams he is not assigned to
        """
        self.user1_team.user = self.user2
        self.user1_team.save()

        response = client.get(self.url)
        assert response.status_code == 404
        assert Team.objects.count() == self.team_count

    def test_no_permission(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestTeamDetailAPIUpdate:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, team_detail_setup):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="change_team"),
        )
        self.user2 = initial_users["user2"]
        self.url = team_detail_setup["url"]
        self.team = team_detail_setup["team"]
        self.user1_team = team_detail_setup["user1_team"]
        self.team_count = team_detail_setup["team_count"]

    def test_user_team(self, client):
        """
        User can see teams he is not assigned to
        """
        response = client.put(self.url, {"name": "Team Edit"})
        assert response.status_code == 200
        assert Team.objects.count() == self.team_count
        assert response.data["name"] == "Team Edit"
        assert response.data["users"] == [self.user1.pk]

        response = client.patch(self.url, {"name": "Team Edit 2"})
        assert response.status_code == 200
        assert Team.objects.count() == self.team_count
        assert response.data["users"] == [self.user1.pk]

    def test_foreign_team(self, client):
        """
        User cannot see teams he is not assigned to
        """
        self.user1_team.user = self.user2
        self.user1_team.save()

        response = client.put(self.url, {"name": "Team Edit"})
        assert response.status_code == 404
        assert Team.objects.count() == self.team_count

        response = client.patch(self.url, {"name": "Team Edit"})
        assert response.status_code == 404
        assert Team.objects.count() == self.team_count

    def test_no_permission(self, client, auth_user2):
        response = client.put(self.url, {"name": "Team Edit"})
        assert response.status_code == 403

        response = client.patch(self.url, {"name": "Team Edit"})
        assert response.status_code == 403


@pytest.mark.django_db
class TestTeamDetailAPIDelete:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, team_detail_setup):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="delete_team"),
        )
        self.user2 = initial_users["user2"]
        self.url = team_detail_setup["url"]
        self.team = team_detail_setup["team"]
        self.user1_team = team_detail_setup["user1_team"]
        self.team_count = team_detail_setup["team_count"]

    def test_user_team(self, client):
        """
        User can see teams he is not assigned to
        """
        response = client.delete(self.url)
        assert response.status_code == 204
        assert Team.objects.count() == self.team_count - 1

    def test_foreign_team(self, client):
        """
        User cannot see teams he is not assigned to
        """
        self.user1_team.user = self.user2
        self.user1_team.save()

        response = client.delete(self.url)
        assert response.status_code == 404
        assert Team.objects.count() == self.team_count

    def test_no_permission(self, client, auth_user2):
        response = client.delete(self.url)
        assert response.status_code == 403
