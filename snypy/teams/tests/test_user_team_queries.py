import pytest

from django.contrib.auth.models import Permission
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from teams.models import Team, UserTeam


@pytest.mark.django_db
class TestUserTeamListQueryCount:
    url = reverse("userteam-list")

    @pytest.fixture(autouse=True)
    def _setup(self, client, initial_users):
        self.users = initial_users
        self.client = client
        self.team = Team.objects.create(name="Team Python")

        initial_users["user1"].user_permissions.add(
            Permission.objects.get(codename="view_userteam"),
        )

        UserTeam.objects.create(user=initial_users["user1"], team=self.team)
        UserTeam.objects.create(user=initial_users["user2"], team=self.team)

    def test_query_count_does_not_scale_with_members(self):
        """
        Listing user teams must not run one query per member (N+1)
        """
        with CaptureQueriesContext(connection) as small_team_queries:
            response = self.client.get(self.url)
            assert response.status_code == 200
            assert len(response.json()) == 2

        UserTeam.objects.create(user=self.users["user3"], team=self.team)
        UserTeam.objects.create(user=self.users["user4"], team=self.team)

        with CaptureQueriesContext(connection) as large_team_queries:
            response = self.client.get(self.url)
            assert response.status_code == 200
            assert len(response.json()) == 4

        assert len(large_team_queries) == len(small_team_queries)
