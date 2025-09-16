import pytest

from django.urls import reverse
from django.contrib.auth.models import Permission

from teams.models import Team, UserTeam
from snippets.models import Label


@pytest.mark.django_db
class TestLabelListAPIView:
    url = reverse("label-list")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_label"),
        )

    def test_view_own_labels(self, client):
        Label.objects.create(name="Test Label 1", user=self.user1)
        Label.objects.create(name="Test Label 2", user=self.user1)
        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_view_other_user_labels(self, client):
        Label.objects.create(name="Other User Label", user=self.user2)
        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_view_team_labels(self, client):
        team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user1, team=team)
        Label.objects.create(name="Team Label", team=team, user=self.user2)
        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_no_permission(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestLabelListAPICreate:
    url = reverse("label-list")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="add_label"),
        )

    def test_create_label_for_user(self, client):
        data = {"name": "Test Label"}
        response = client.post(self.url, data)
        assert response.status_code == 201
        assert Label.objects.count() == 1
        label = Label.objects.first()
        assert label.name == "Test Label"
        assert label.user == self.user1
        assert label.team is None

    def test_create_label_for_team(self, client):
        team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user1, team=team)
        data = {"name": "Test Label", "team": team.pk}
        response = client.post(self.url, data)
        assert response.status_code == 201
        assert Label.objects.count() == 1
        label = Label.objects.first()
        assert label.name == "Test Label"
        assert label.user == self.user1
        assert label.team == team

    def test_no_permission(self, client, auth_user2):
        data = {"name": "Test Label"}
        response = client.post(self.url, data)
        assert response.status_code == 403


@pytest.fixture
def label_detail_setup(initial_users):
    user1 = initial_users["user1"]
    label = Label.objects.create(name="Test Label", user=user1)
    url = reverse("label-detail", kwargs={"pk": label.pk})
    return {"url": url, "label": label}


@pytest.mark.django_db
class TestLabelDetailAPIView:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, label_detail_setup):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="view_label"))
        self.user2.user_permissions.add(Permission.objects.get(codename="view_label"))
        self.url = label_detail_setup["url"]
        self.label = label_detail_setup["label"]

    def test_view_own_label(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Label"

    def test_view_other_user_label(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestLabelDetailAPIUpdate:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, label_detail_setup):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="change_label"))
        self.url = label_detail_setup["url"]
        self.label = label_detail_setup["label"]

    def test_update_own_label(self, client):
        data = {"name": "Updated Label"}
        response = client.put(self.url, data)
        assert response.status_code == 200
        self.label.refresh_from_db()
        assert self.label.name == "Updated Label"

    def test_update_other_user_label(self, client, auth_user2):
        data = {"name": "Updated Label"}
        response = client.put(self.url, data)
        assert response.status_code == 404


@pytest.mark.django_db
class TestLabelDetailAPIDelete:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users, label_detail_setup):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="delete_label"))
        self.url = label_detail_setup["url"]
        self.label = label_detail_setup["label"]

    def test_delete_own_label(self, client):
        response = client.delete(self.url)
        assert response.status_code == 204
        assert Label.objects.count() == 0

    def test_delete_other_user_label(self, client, auth_user2):
        response = client.delete(self.url)
        assert response.status_code == 404
        assert Label.objects.count() == 1


@pytest.mark.django_db
class TestLabelFilter:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="view_label"))

        # User1 label
        Label.objects.create(name="User 1 Label", user=self.user1)
        # Team1 label for user1
        team1 = Team.objects.create(name="Test Team 1")
        UserTeam.objects.create(user=self.user1, team=team1)
        Label.objects.create(name="Team 1 Label", team=team1, user=self.user1)
        # User2 label
        Label.objects.create(name="User 2 Label", user=self.user2)
        # Team2 label for user2
        team2 = Team.objects.create(name="Test Team 2")
        UserTeam.objects.create(user=self.user2, team=team2)
        Label.objects.create(name="Team 2 Label", team=team2, user=self.user2)

        self.url = reverse("label-list")

    def test_filter_by_user(self, client):
        response = client.get(self.url, {"user": self.user1.pk})
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "User 1 Label"

    def test_filter_by_team(self, client):
        team = Team.objects.get(name="Test Team 1")
        response = client.get(self.url, {"team": team.pk})
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Team 1 Label"
