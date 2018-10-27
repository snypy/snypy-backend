import json
import unittest

from django.contrib.auth.models import Permission
from django.urls import reverse

from core.tests import BaseAPITestCase
from snippets.models import Snippet
from teams.models import Team, UserTeam


class BaseTeamApiTestCase(BaseAPITestCase):

    url = reverse("snippet-list")

    def setUp(self):
        super().setUp()

        # Initial Snippets for each user
        Snippet.objects.create(user=self.user1, title="Python snippet user 1")
        Snippet.objects.create(user=self.user2, title="Python snippet user 2")

        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")


class TeamSnippetListAPIViewTestCase(BaseTeamApiTestCase):

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename='view_snippet'))
        self.user2.user_permissions.add(Permission.objects.get(codename='view_snippet'))

    def test_team_snippet(self):
        """
        User should see snippets that are assigned to him
        """
        Snippet.objects.create(user=self.user1, title="Python snippet team 1", team=self.team1)

        team_1_member_count = UserTeam.objects.filter(team=self.team1).count()
        self.assertEquals(team_1_member_count, 0)

        team_2_member_count = UserTeam.objects.filter(team=self.team2).count()
        self.assertEquals(team_2_member_count, 0)

        # Snippet is visible to owner
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 2)

        response = self.client.get("%s?team_is_null=True" % self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 1)

        response = self.client.get("%s?team=%d" % (self.url, self.team1.pk))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 1)

        response = self.client.get("%s?team=%d" % (self.url, self.team2.pk))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 0)

        # But not to other users
        self.api_authentication(self.token2)

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 1)

        response = self.client.get("%s?team_is_null=True" % self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 1)

        response = self.client.get("%s?team=%d" % (self.url, self.team1.pk))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 0)

        response = self.client.get("%s?team=%d" % (self.url, self.team2.pk))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 0)

        # Only if they belong to the group of the snippet
        UserTeam.objects.create(team=self.team1, user=self.user2)

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 2)

        response = self.client.get("%s?team_is_null=True" % self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 1)

        response = self.client.get("%s?team=%d" % (self.url, self.team1.pk))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 1)

        response = self.client.get("%s?team=%d" % (self.url, self.team2.pk))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 0)


class TeamSnippetListAPICreateTestCase(BaseTeamApiTestCase):

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename='add_snippet'))
        self.user2.user_permissions.add(Permission.objects.get(codename='add_snippet'))

    @unittest.skip("Not implemented")
    def test_team_snippet(self):
        pass


class TeamSnippetDetailAPIViewTestCase(BaseTeamApiTestCase):
    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename='view_snippet'))
        self.user2.user_permissions.add(Permission.objects.get(codename='view_snippet'))

    @unittest.skip("Not implemented")
    def test_team_snippet(self):
        pass


class TeamSnippetDetailAPIEditTestCase(BaseTeamApiTestCase):
    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename='change_snippet'))
        self.user2.user_permissions.add(Permission.objects.get(codename='change_snippet'))

    @unittest.skip("Not implemented")
    def test_team_snippet(self):
        pass


class TeamSnippetDetailAPIDeleteTestCase(BaseTeamApiTestCase):
    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename='delete_snippet'))
        self.user2.user_permissions.add(Permission.objects.get(codename='delete_snippet'))

    @unittest.skip("Not implemented")
    def test_team_snippet(self):
        pass
