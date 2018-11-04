import json

from django.contrib.auth.models import Permission
from django.urls import reverse

from core.tests import BaseAPITestCase
from teams.models import Team, UserTeam


class TeamUserListAPIBaseTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.team = Team.objects.create(name="Team Python")
        self.team_count = Team.objects.count()


class TeamUserListAPIViewTestCase(TeamUserListAPIBaseTestCase):
    url = reverse("userteam-list")

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename='view_userteam'),
        )

    def test_user_userteam(self):
        """
        User can see his team assignments
        """
        userteam_count = UserTeam.objects.count()
        userteam = UserTeam.objects.create(user=self.user1, team=self.team)

        for role in UserTeam.ROLES:
            userteam.role = role
            userteam.save()

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(json.loads(response.content)), userteam_count + 1)

    def test_foreign_user_userteam(self):
        """
        User cannot see other team assignments
        """
        userteam_count = UserTeam.objects.count()
        userteam = UserTeam.objects.create(user=self.user2, team=self.team)

        for role in UserTeam.ROLES:
            userteam.role = role
            userteam.save()

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(json.loads(response.content)), userteam_count)

    def test_foreign_user_userteam_assigned_team(self):
        """
        User can see other team assignments of team he is assigned to
        """
        userteam_count = UserTeam.objects.count()
        userteam1 = UserTeam.objects.create(user=self.user1, team=self.team)
        userteam2 = UserTeam.objects.create(user=self.user2, team=self.team)

        for role1 in UserTeam.ROLES:
            userteam1.role = role1
            userteam1.save()

            for role2 in UserTeam.ROLES:
                userteam2.role = role2
                userteam2.save()

                response = self.client.get(self.url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(json.loads(response.content)), userteam_count + 2)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class TeamUserListAPICreateTestCase(TeamUserListAPIBaseTestCase):
    url = reverse("userteam-list")

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename='add_userteam'),
        )

    def test_with_no_assignment(self):
        response = self.client.post(self.url, {'user': self.user2.pk, 'team': self.team.pk})
        self.assertEqual(response.status_code, 400)

    def test_with_assignment_subscriber(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_SUBSCRIBER)

        response = self.client.post(self.url, {'user': self.user2.pk, 'team': self.team.pk})
        self.assertEqual(response.status_code, 400)

    def test_with_assignment_contributor(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_CONTRIBUTOR)

        response = self.client.post(self.url, {'user': self.user2.pk, 'team': self.team.pk})
        self.assertEqual(response.status_code, 400)

    def test_with_assignment_editor(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_EDITOR)

        response = self.client.post(self.url, {'user': self.user2.pk, 'team': self.team.pk})
        self.assertEqual(response.status_code, 201)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.post(self.url, {'user': self.user2.pk, 'team': self.team.pk})
        self.assertEqual(response.status_code, 403)


class TeamUserDetailAPIBaseTestCase(TeamUserListAPIBaseTestCase):

    def setUp(self):
        super().setUp()

        self.team = Team.objects.create(name="Team Python")
        self.team_count = Team.objects.count()

        self.userteam = UserTeam.objects.create(user=self.user1, team=self.team)
        self.userteam_count = UserTeam.objects.count()
        self.url = reverse("userteam-detail", kwargs={'pk': self.userteam.pk})


class TeamUserDetailAPIViewTestCase(TeamUserDetailAPIBaseTestCase):

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename='view_userteam'),
        )

    def test_user_userteam(self):
        """
        User can see his team assignments
        """
        for role in UserTeam.ROLES:
            self.userteam.role = role
            self.userteam.save()

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

    def test_foreign_user_userteam(self):
        """
        User cannot see other team assignments
        """
        for role in UserTeam.ROLES:
            self.userteam.user = self.user2
            self.userteam.role = role
            self.userteam.save()

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 404)

    def test_foreign_user_userteam_assigned_team(self):
        """
        User can see other team assignments of team he is assigned to
        """
        userteam2 = UserTeam.objects.create(user=self.user2, team=self.team)
        url2 = reverse("userteam-detail", kwargs={'pk': userteam2.pk})

        for role1 in UserTeam.ROLES:
            self.userteam.role = role1
            self.userteam.save()

            for role2 in UserTeam.ROLES:
                userteam2.role = role2
                userteam2.save()

                response = self.client.get(url2)
                self.assertEqual(response.status_code, 200)

    def test_no_permission(self):
        self.api_authentication(self.token2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class TeamUserDetailAPIUpdateTestCase(TeamUserDetailAPIBaseTestCase):

    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename='change_userteam'),
        )
        self.userteam.user = self.user2
        self.userteam.save()

        self.edit_data = {
            'role': UserTeam.ROLE_EDITOR,
            'team': self.team.pk,
            'user': self.user2.pk
        }

    def test_with_no_assignment(self):
        response = self.client.put(self.url, self.edit_data)
        self.assertEqual(response.status_code, 404)

    def test_with_assignment_subscriber(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_SUBSCRIBER)

        response = self.client.put(self.url, self.edit_data)
        self.assertEqual(response.status_code, 403)

        response = self.client.patch(self.url, {'role': UserTeam.ROLE_EDITOR})
        self.assertEqual(response.status_code, 403)

    def test_with_assignment_contributor(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_CONTRIBUTOR)

        response = self.client.put(self.url, self.edit_data)
        self.assertEqual(response.status_code, 403)

        response = self.client.patch(self.url, {'role': UserTeam.ROLE_EDITOR})
        self.assertEqual(response.status_code, 403)

    def test_with_assignment_editor(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_EDITOR)

        response = self.client.put(self.url, self.edit_data)
        self.assertEqual(response.status_code, 200)

        response = self.client.patch(self.url, {'role': UserTeam.ROLE_EDITOR})
        self.assertEqual(response.status_code, 200)

        self.assertEquals(response.data['role'], UserTeam.ROLE_EDITOR)

    def test_change_user(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_EDITOR)
        self.edit_data['user'] = self.user3.pk

        response = self.client.put(self.url, self.edit_data)
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(self.url, {'user': self.user3.pk})
        self.assertEqual(response.status_code, 400)

    def test_change_team(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_EDITOR)
        team = Team.objects.create(name="Test Team")
        self.edit_data['team'] = team.pk

        response = self.client.put(self.url, self.edit_data)
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(self.url, {'team': team.pk})
        self.assertEqual(response.status_code, 400)

    def test_no_permission(self):
        self.api_authentication(self.token2)

        response = self.client.put(self.url, self.edit_data)
        self.assertEqual(response.status_code, 403)

        response = self.client.patch(self.url, self.edit_data)
        self.assertEqual(response.status_code, 403)


class TeamUserDetailAPIDeleteTestCase(TeamUserDetailAPIBaseTestCase):
    def setUp(self):
        super().setUp()

        self.user1.user_permissions.add(
            Permission.objects.get(codename='delete_userteam'),
        )
        self.userteam.user = self.user2
        self.userteam.save()

    def test_with_no_assignment(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)

    def test_with_assignment_subscriber(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_SUBSCRIBER)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)

    def test_with_assignment_contributor(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_CONTRIBUTOR)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)

    def test_with_assignment_editor(self):
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_EDITOR)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)

    def test_no_permission(self):
        self.api_authentication(self.token2)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
