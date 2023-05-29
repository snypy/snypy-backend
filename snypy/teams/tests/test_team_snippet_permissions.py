import json

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

        self.team1_snippet = Snippet.objects.create(user=self.user1, title="Python snippet team 1", team=self.team1)

        team_1_member_count = UserTeam.objects.filter(team=self.team1).count()
        self.assertEquals(team_1_member_count, 0)

        team_2_member_count = UserTeam.objects.filter(team=self.team2).count()
        self.assertEquals(team_2_member_count, 0)


class TeamSnippetListAPIViewTestCase(BaseTeamApiTestCase):
    """
    Snippets can be viewable by their owner and by users that belong to the same team
    that the snippet is assigned to. The visibility of the snippets is not related to the role in the team.
    """

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename="view_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="view_snippet"))

    def test_team_snippet_owner(self):
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

    def test_team_snippet_other_user_unassigned(self):
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

    def test_team_snippet_other_user_assigned_as_subscriber(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_SUBSCRIBER)

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

    def test_team_snippet_other_user_assigned_as_contributor(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_CONTRIBUTOR)

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

    def test_team_snippet_other_user_assigned_as_editor(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_EDITOR)

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
    """
    Snippets can be added only on teams the user is assigned when to role is contributor or editor.
    """

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename="add_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="add_snippet"))

        self.create_data = {
            "title": "Python snippet",
            "description": "",
            "team": self.team1.pk,
        }

    def assert_create_response(self, response):
        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.data["user"], self.user1.pk)
        self.assertEqual(response.data["title"], self.create_data["title"])
        self.assertEqual(response.data["description"], self.create_data["description"])
        self.assertEqual(response.data["visibility"], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data["team"], self.team1.pk)
        self.assertEqual(response.data["user_display"], self.user1.username)
        self.assertListEqual(response.data["files"], [])
        self.assertListEqual(response.data["labels"], [])

    def test_team_snippet_unassigned(self):
        response = self.client.post(self.url, self.create_data)
        self.assertEqual(response.status_code, 400)

    def test_team_snippet_other_user_assigned_subscriber(self):
        UserTeam.objects.create(team=self.team1, user=self.user1, role=UserTeam.ROLE_SUBSCRIBER)
        response = self.client.post(self.url, self.create_data)
        self.assertEqual(response.status_code, 400)

    def test_team_snippet_other_user_assigned_contributor(self):
        UserTeam.objects.create(team=self.team1, user=self.user1, role=UserTeam.ROLE_CONTRIBUTOR)
        response = self.client.post(self.url, self.create_data)
        self.assert_create_response(response)

    def test_team_snippet_other_user_assigned_editor(self):
        UserTeam.objects.create(team=self.team1, user=self.user1, role=UserTeam.ROLE_EDITOR)
        response = self.client.post(self.url, self.create_data)
        self.assert_create_response(response)


class TeamSnippetDetailAPIViewTestCase(BaseTeamApiTestCase):
    """
    Snippets can be viewable by their owner and by users that belong to the same team
    that the snippet is assigned to. The visibility of the snippets is not related to the role in the team.
    """

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename="view_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="view_snippet"))

        self.url = reverse("snippet-detail", kwargs={"pk": self.team1_snippet.pk})

    def test_team_snippet_owner(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_team_snippet_other_user_unassigned(self):
        self.api_authentication(self.token2)

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 404)

    def test_team_snippet_other_user_assigned_as_subscriber(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_SUBSCRIBER)

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_team_snippet_other_user_assigned_as_contributor(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_CONTRIBUTOR)

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_team_snippet_other_user_assigned_as_editor(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_EDITOR)

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)


class TeamSnippetDetailAPIEditTestCase(BaseTeamApiTestCase):
    """
    Snippets can be edited only on teams the user is assigned to with the role editor.
    """

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename="change_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="change_snippet"))

        self.url = reverse("snippet-detail", kwargs={"pk": self.team1_snippet.pk})
        self.patch_data = {"title": "Python snippet edited"}

    def assert_patch_response(self, response):
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["user"], self.user1.pk)
        self.assertEqual(response.data["title"], self.patch_data["title"])
        self.assertEqual(response.data["description"], "")
        self.assertEqual(response.data["visibility"], Snippet.VISIBILITY_PRIVATE)
        self.assertEqual(response.data["team"], self.team1.pk)
        self.assertEqual(response.data["user_display"], self.user1.username)
        self.assertListEqual(response.data["files"], [])
        self.assertListEqual(response.data["labels"], [])

    def test_team_snippet_owner(self):
        response = self.client.patch(self.url, self.patch_data)
        self.assert_patch_response(response)

    def test_team_snippet_other_user_unassigned(self):
        self.api_authentication(self.token2)

        response = self.client.patch(self.url, self.patch_data)
        self.assertEquals(response.status_code, 404)

    def test_team_snippet_other_user_assigned_as_subscriber(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_SUBSCRIBER)

        response = self.client.patch(self.url, self.patch_data)
        self.assertEquals(response.status_code, 403)

    def test_team_snippet_other_user_assigned_as_contributor(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_CONTRIBUTOR)

        response = self.client.patch(self.url, self.patch_data)
        self.assertEquals(response.status_code, 403)

    def test_team_snippet_other_user_assigned_as_editor(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_EDITOR)

        response = self.client.patch(self.url, self.patch_data)
        self.assert_patch_response(response)


class TeamSnippetDetailAPIDeleteTestCase(BaseTeamApiTestCase):
    """
    Snippets can be deleted only on teams the user is assigned to with the role editor.
    """

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(Permission.objects.get(codename="delete_snippet"))
        self.user2.user_permissions.add(Permission.objects.get(codename="delete_snippet"))

        self.url = reverse("snippet-detail", kwargs={"pk": self.team1_snippet.pk})

    def test_team_snippet_owner(self):
        response = self.client.delete(self.url)
        self.assertEquals(response.status_code, 204)

    def test_team_snippet_other_user_unassigned(self):
        self.api_authentication(self.token2)

        response = self.client.delete(self.url)
        self.assertEquals(response.status_code, 404)

    def test_team_snippet_other_user_assigned_as_subscriber(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_SUBSCRIBER)

        response = self.client.delete(self.url)
        self.assertEquals(response.status_code, 403)

    def test_team_snippet_other_user_assigned_as_contributor(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_CONTRIBUTOR)

        response = self.client.delete(self.url)
        self.assertEquals(response.status_code, 403)

    def test_team_snippet_other_user_assigned_as_editor(self):
        self.api_authentication(self.token2)
        UserTeam.objects.create(team=self.team1, user=self.user2, role=UserTeam.ROLE_EDITOR)

        response = self.client.delete(self.url)
        self.assertEquals(response.status_code, 204)
