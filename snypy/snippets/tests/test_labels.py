import pytest

from django.urls import reverse
from django.contrib.auth.models import Permission

from teams.models import Team, UserTeam
from snippets.models import Label, Snippet, SnippetLabel


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

    @pytest.mark.parametrize("role", [UserTeam.ROLE_EDITOR, UserTeam.ROLE_CONTRIBUTOR])
    def test_create_label_for_team(self, client, role):
        team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user1, team=team, role=role)
        data = {"name": "Test Label", "team": team.pk}
        response = client.post(self.url, data)
        assert response.status_code == 201
        assert Label.objects.count() == 1
        label = Label.objects.first()
        assert label.name == "Test Label"
        assert label.user == self.user1
        assert label.team == team

    def test_create_label_for_team_as_subscriber(self, client):
        team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user1, team=team, role=UserTeam.ROLE_SUBSCRIBER)
        data = {"name": "Test Label", "team": team.pk}
        response = client.post(self.url, data)
        assert response.status_code == 400
        assert "team" in response.json()
        assert Label.objects.count() == 0

    def test_create_label_for_team_as_non_member(self, client):
        team = Team.objects.create(name="Test Team")
        data = {"name": "Test Label", "team": team.pk}
        response = client.post(self.url, data)
        assert response.status_code == 400
        assert "team" in response.json()
        assert Label.objects.count() == 0

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
        self.user2.user_permissions.add(Permission.objects.get(codename="change_label"))
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
        self.user2.user_permissions.add(Permission.objects.get(codename="delete_label"))
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


@pytest.mark.django_db
class TestTeamLabelPermissions:
    """
    Team labels are visible to every member; changing them requires the CONTRIBUTOR or EDITOR role.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_label"),
            Permission.objects.get(codename="change_label"),
            Permission.objects.get(codename="delete_label"),
        )
        self.team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user2, team=self.team, role=UserTeam.ROLE_EDITOR)
        self.label = Label.objects.create(name="Team Label", team=self.team, user=self.user2)
        self.url = reverse("label-detail", kwargs={"pk": self.label.pk})

    def _join(self, role):
        if role is not None:
            UserTeam.objects.create(user=self.user1, team=self.team, role=role)

    @pytest.mark.parametrize(
        "role,status_code",
        [
            (UserTeam.ROLE_EDITOR, 200),
            (UserTeam.ROLE_CONTRIBUTOR, 200),
            (UserTeam.ROLE_SUBSCRIBER, 200),
            (None, 404),
        ],
    )
    def test_detail(self, client, role, status_code):
        self._join(role)
        response = client.get(self.url)
        assert response.status_code == status_code
        if status_code == 200:
            assert response.json()["name"] == "Team Label"
            assert response.json()["team"] == self.team.pk

    @pytest.mark.parametrize(
        "role,status_code",
        [
            (UserTeam.ROLE_EDITOR, 200),
            (UserTeam.ROLE_CONTRIBUTOR, 200),
            (UserTeam.ROLE_SUBSCRIBER, 403),
            (None, 404),
        ],
    )
    def test_update(self, client, role, status_code):
        self._join(role)
        response = client.put(self.url, {"name": "Updated Label", "team": self.team.pk})
        assert response.status_code == status_code
        self.label.refresh_from_db()
        assert self.label.name == ("Updated Label" if status_code == 200 else "Team Label")
        assert self.label.team == self.team

    @pytest.mark.parametrize(
        "role,status_code",
        [
            (UserTeam.ROLE_EDITOR, 200),
            (UserTeam.ROLE_CONTRIBUTOR, 200),
            (UserTeam.ROLE_SUBSCRIBER, 403),
            (None, 404),
        ],
    )
    def test_partial_update(self, client, role, status_code):
        self._join(role)
        response = client.patch(self.url, {"name": "Updated Label"})
        assert response.status_code == status_code
        self.label.refresh_from_db()
        assert self.label.name == ("Updated Label" if status_code == 200 else "Team Label")

    @pytest.mark.parametrize(
        "role,status_code",
        [
            (UserTeam.ROLE_EDITOR, 204),
            (UserTeam.ROLE_CONTRIBUTOR, 204),
            (UserTeam.ROLE_SUBSCRIBER, 403),
            (None, 404),
        ],
    )
    def test_delete(self, client, role, status_code):
        self._join(role)
        response = client.delete(self.url)
        assert response.status_code == status_code
        assert Label.objects.filter(pk=self.label.pk).exists() == (status_code != 204)

    def test_creator_demoted_to_subscriber(self, client):
        """
        The role decides, not who created the label
        """
        self.label.user = self.user1
        self.label.save()
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_SUBSCRIBER)
        response = client.patch(self.url, {"name": "Updated Label"})
        assert response.status_code == 403
        response = client.delete(self.url)
        assert response.status_code == 403
        assert Label.objects.filter(pk=self.label.pk).exists()

    def test_removed_member(self, client):
        user_team = UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_EDITOR)
        response = client.get(reverse("label-list"))
        assert [label["pk"] for label in response.json()] == [self.label.pk]

        user_team.delete()

        response = client.get(reverse("label-list"))
        assert response.status_code == 200
        assert response.json() == []
        assert client.get(self.url).status_code == 404
        assert client.patch(self.url, {"name": "Updated Label"}).status_code == 404
        assert client.delete(self.url).status_code == 404
        assert Label.objects.filter(pk=self.label.pk).exists()


@pytest.mark.django_db
class TestTeamLabelSnippetCount:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(Permission.objects.get(codename="view_label"))

        self.team = Team.objects.create(name="Test Team")
        other_team = Team.objects.create(name="Other Team")
        foreign_team = Team.objects.create(name="Foreign Team")
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_SUBSCRIBER)
        UserTeam.objects.create(user=self.user1, team=other_team, role=UserTeam.ROLE_SUBSCRIBER)
        UserTeam.objects.create(user=self.user2, team=foreign_team, role=UserTeam.ROLE_EDITOR)

        self.label = Label.objects.create(name="Team Label", team=self.team, user=self.user2)
        other_label = Label.objects.create(name="Other Team Label", team=other_team, user=self.user2)

        # Two labelled snippets and one unlabelled snippet in the team
        for title in ("Team Snippet 1", "Team Snippet 2"):
            snippet = Snippet.objects.create(user=self.user2, team=self.team, title=title)
            SnippetLabel.objects.create(snippet=snippet, label=self.label)
        Snippet.objects.create(user=self.user2, team=self.team, title="Unlabelled Team Snippet")

        # Snippets of another team the user is in, labelled with that team's label
        for title in ("Other Team Snippet 1", "Other Team Snippet 2", "Other Team Snippet 3"):
            snippet = Snippet.objects.create(user=self.user2, team=other_team, title=title)
            SnippetLabel.objects.create(snippet=snippet, label=other_label)

        # A snippet the user cannot see, even though it carries the team label
        snippet = Snippet.objects.create(user=self.user2, team=foreign_team, title="Foreign Snippet")
        SnippetLabel.objects.create(snippet=snippet, label=self.label)

    def test_snippet_count(self, client):
        response = client.get(reverse("label-detail", kwargs={"pk": self.label.pk}))
        assert response.status_code == 200
        assert response.json()["snippet_count"] == 2

    def test_snippet_count_in_list(self, client):
        response = client.get(reverse("label-list"))
        assert response.status_code == 200
        counts = {label["name"]: label["snippet_count"] for label in response.json()}
        assert counts == {"Team Label": 2, "Other Team Label": 3}
