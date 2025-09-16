from django.urls import reverse
from rest_framework.test import APITestCase

from core.tests.factories import UserFactory
from teams.models import Team, UserTeam
from snippets.models import Label


class LabelAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_create_label_for_user(self):
        url = reverse("label-list")
        data = {"name": "Test Label"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Label.objects.count(), 1)
        label = Label.objects.first()
        self.assertEqual(label.name, "Test Label")
        self.assertEqual(label.user, self.user)
        self.assertIsNone(label.team)

    def test_create_label_for_team(self):
        team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user, team=team)
        url = reverse("label-list")
        data = {"name": "Test Label", "team": team.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Label.objects.count(), 1)
        label = Label.objects.first()
        self.assertEqual(label.name, "Test Label")
        self.assertEqual(label.user, self.user)
        self.assertEqual(label.team, team)

    def test_view_own_labels(self):
        Label.objects.create(name="Test Label 1", user=self.user)
        Label.objects.create(name="Test Label 2", user=self.user)
        url = reverse("label-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_view_other_user_labels(self):
        other_user = UserFactory()
        Label.objects.create(name="Other User Label", user=other_user)
        url = reverse("label-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_view_team_labels(self):
        team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user, team=team)
        Label.objects.create(name="Team Label", team=team, user=UserFactory())
        url = reverse("label-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_label_viewable_queryset(self):
        # Own label
        Label.objects.create(name="Own Label", user=self.user)
        # Other user's label
        Label.objects.create(name="Other User Label", user=UserFactory())
        # Team label
        team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user, team=team)
        Label.objects.create(name="Team Label", team=team, user=UserFactory())

        self.assertEqual(Label.objects.viewable().count(), 2)

    def test_update_own_label(self):
        label = Label.objects.create(name="Test Label", user=self.user)
        url = reverse("label-detail", kwargs={"pk": label.pk})
        data = {"name": "Updated Label"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        label.refresh_from_db()
        self.assertEqual(label.name, "Updated Label")

    def test_update_other_user_label(self):
        other_user = UserFactory()
        label = Label.objects.create(name="Other User Label", user=other_user)
        url = reverse("label-detail", kwargs={"pk": label.pk})
        data = {"name": "Updated Label"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 404)

    def test_delete_own_label(self):
        label = Label.objects.create(name="Test Label", user=self.user)
        url = reverse("label-detail", kwargs={"pk": label.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Label.objects.count(), 0)

    def test_delete_other_user_label(self):
        other_user = UserFactory()
        label = Label.objects.create(name="Other User Label", user=other_user)
        url = reverse("label-detail", kwargs={"pk": label.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Label.objects.count(), 1)

    def test_filter_by_user(self):
        # User label
        Label.objects.create(name="User Label", user=self.user)
        # Team label
        team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user, team=team)
        Label.objects.create(name="Team Label", team=team, user=self.user)
        # Other user's label
        Label.objects.create(name="Other User Label", user=UserFactory())

        url = reverse("label-list")
        response = self.client.get(url, {"user": self.user.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "User Label")

    def test_filter_by_team(self):
        # Team 1 label
        team1 = Team.objects.create(name="Test Team 1")
        UserTeam.objects.create(user=self.user, team=team1)
        Label.objects.create(name="Team 1 Label", team=team1, user=self.user)
        # Team 2 label
        team2 = Team.objects.create(name="Test Team 2")
        UserTeam.objects.create(user=self.user, team=team2)
        Label.objects.create(name="Team 2 Label", team=team2, user=self.user)

        url = reverse("label-list")
        response = self.client.get(url, {"team": team1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Team 1 Label")
