import json

from django.contrib.auth.models import Permission
from django.urls import reverse

from core.tests import BaseAPITestCase
from teams.models import Team, UserTeam


class TeamListAPIViewTestCase(BaseAPITestCase):

    url = reverse("team-list")

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_team"),
        )

    def test_user_team(self):
        """
        User can see teams he is assigned to
        """
        team_count = Team.objects.count()
        team = Team.objects.create(name="Team Python")
        UserTeam.objects.create(user=self.user1, team=team)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), team_count + 1)

    def test_foreign_team(self):
        """
        User cannot see teams he is not assigned to
        """
        team_count = Team.objects.count()
        Team.objects.create(name="Team Python")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), team_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class TeamListAPICreateTestCase(BaseAPITestCase):

    url = reverse("team-list")
    create_data = {
        "name": "Team Python",
    }

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="add_team"),
        )

    def assert_create_response(self, response):
        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.data["name"], self.create_data["name"])
        self.assertEqual(response.data["users"], [self.user1.pk])

    def test_user_team(self):
        response = self.client.post(self.url, self.create_data)
        self.assert_create_response(response)

    def test_minimum_fields(self):
        """
        Create a new team by sending minimal fields in payload
        """
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

        data["name"] = self.create_data["name"]
        response = self.client.post(self.url, data)
        self.assert_create_response(response)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.post(self.url, self.create_data)
        self.assertEqual(response.status_code, 403)


class TeamDetailAPIBaseTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.team = Team.objects.create(name="Team Python")
        self.user1_team = UserTeam.objects.create(user=self.user1, team=self.team)

        self.url = reverse("team-detail", kwargs={"pk": self.team.pk})
        self.team_count = Team.objects.count()


class TeamDetailAPIViewTestCase(TeamDetailAPIBaseTestCase):
    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_team"),
        )

    def test_user_team(self):
        """
        User can see teams he is not assigned to
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Team.objects.count(), self.team_count)

        self.assertEqual(response.data["name"], "Team Python")
        self.assertEqual(response.data["users"], [self.user1.pk])

    def test_foreign_team(self):
        """
        User cannot see teams he is not assigned to
        """
        self.user1_team.user = self.user2
        self.user1_team.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Team.objects.count(), self.team_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class TeamDetailAPIUpdateTestCase(TeamDetailAPIBaseTestCase):
    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="change_team"),
        )

    def test_user_team(self):
        """
        User can see teams he is not assigned to
        """
        response = self.client.put(self.url, {"name": "Team Edit"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Team.objects.count(), self.team_count)

        self.assertEqual(response.data["name"], "Team Edit")
        self.assertEqual(response.data["users"], [self.user1.pk])
        self.assertEqual(Team.objects.count(), self.team_count)

        response = self.client.patch(self.url, {"name": "Team Edit 2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Team.objects.count(), self.team_count)

        self.assertEqual(response.data["name"], "Team Edit 2")
        self.assertEqual(response.data["users"], [self.user1.pk])
        self.assertEqual(Team.objects.count(), self.team_count)

    def test_foreign_team(self):
        """
        User cannot see teams he is not assigned to
        """
        self.user1_team.user = self.user2
        self.user1_team.save()

        response = self.client.put(self.url, {"name": "Team Edit"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Team.objects.count(), self.team_count)

        response = self.client.patch(self.url, {"name": "Team Edit"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Team.objects.count(), self.team_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.put(self.url, {"name": "Team Edit"})
        self.assertEqual(response.status_code, 403)

        self.api_authentication(self.token2)
        response = self.client.patch(self.url, {"name": "Team Edit"})
        self.assertEqual(response.status_code, 403)


class TeamDetailAPIDeleteTestCase(TeamDetailAPIBaseTestCase):
    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename="delete_team"),
        )

    def test_user_team(self):
        """
        User can see teams he is not assigned to
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Team.objects.count(), self.team_count - 1)

    def test_foreign_team(self):
        """
        User cannot see teams he is not assigned to
        """
        self.user1_team.user = self.user2
        self.user1_team.save()

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Team.objects.count(), self.team_count)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
