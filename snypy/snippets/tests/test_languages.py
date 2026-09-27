import pytest

from django.urls import reverse

from teams.models import Team, UserTeam
from snippets.models import File, Language, Snippet


@pytest.mark.django_db
class TestLanguageSnippetCount:
    url = reverse("language-list")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.python = Language.objects.create(name="Python")
        self.team = Team.objects.create(name="Test Team")
        UserTeam.objects.create(user=self.user1, team=self.team, role=UserTeam.ROLE_EDITOR)

    def _create_snippet(self, user, languages, team=None, visibility=Snippet.VISIBILITY_PRIVATE):
        snippet = Snippet.objects.create(title="Snippet", user=user, team=team, visibility=visibility)
        for index, language in enumerate(languages):
            File.objects.create(snippet=snippet, language=language, name=f"file{index}")
        return snippet

    def _count(self, client, params=None):
        response = client.get(self.url, params or {})
        assert response.status_code == 200
        return {item["name"]: item["snippet_count"] for item in response.json()}["Python"]

    def test_multiple_files_same_language_count_once(self, client):
        self._create_snippet(self.user1, [self.python, self.python, self.python])
        assert self._count(client) == 1

    def test_counts_each_snippet(self, client):
        self._create_snippet(self.user1, [self.python, self.python])
        self._create_snippet(self.user1, [self.python])
        assert self._count(client) == 2

    def test_not_viewable_snippets_not_counted(self, client):
        self._create_snippet(self.user2, [self.python, self.python])
        assert self._count(client) == 0

    def test_public_snippets_of_other_users_counted(self, client):
        self._create_snippet(self.user2, [self.python, self.python], visibility=Snippet.VISIBILITY_PUBLIC)
        assert self._count(client) == 1

    def test_filter_by_team(self, client):
        self._create_snippet(self.user1, [self.python, self.python], team=self.team)
        self._create_snippet(self.user2, [self.python], team=self.team)
        self._create_snippet(self.user1, [self.python])
        other_team = Team.objects.create(name="Other Team")
        self._create_snippet(self.user2, [self.python], team=other_team, visibility=Snippet.VISIBILITY_PUBLIC)
        assert self._count(client, {"team": self.team.pk}) == 2
        assert self._count(client, {"team": other_team.pk}) == 1

    def test_filter_by_user(self, client):
        self._create_snippet(self.user1, [self.python, self.python])
        self._create_snippet(self.user1, [self.python], team=self.team)
        self._create_snippet(self.user2, [self.python], visibility=Snippet.VISIBILITY_PUBLIC)
        assert self._count(client, {"user": self.user1.pk}) == 1
        assert self._count(client, {"user": self.user2.pk}) == 1
