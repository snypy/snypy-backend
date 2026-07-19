import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from snippets.models import Snippet, File, Label, Language, SnippetLabel


@pytest.fixture
def snippet_with_relations(initial_users):
    snippet = Snippet.objects.create(
        user=initial_users["user1"],
        title="Sort dict by value",
        description="One-liner",
        visibility=Snippet.VISIBILITY_PRIVATE,
    )
    language = Language.objects.create(name="Python")
    File.objects.create(snippet=snippet, language=language, name="sort.py", content="sorted(d, key=d.get)")
    label = Label.objects.create(name="python", user=initial_users["user1"])
    SnippetLabel.objects.create(snippet=snippet, label=label)
    yield snippet


@pytest.mark.django_db
class TestSnippetExportSerializer:
    def test_serializes_names_not_pks(self, snippet_with_relations):
        from snippets.rest.serializers import SnippetExportSerializer

        data = SnippetExportSerializer(snippet_with_relations).data

        assert data["title"] == "Sort dict by value"
        assert data["description"] == "One-liner"
        assert data["visibility"] == "PRIVATE"
        assert data["labels"] == ["python"]
        assert data["files"] == [{"name": "sort.py", "language": "Python", "content": "sorted(d, key=d.get)"}]
        assert "pk" not in data
        assert "user" not in data
        assert "created_date" in data
        assert "modified_date" in data


@pytest.mark.django_db
class TestSnippetExportEndpoint:
    url = reverse("snippet-export")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user2 = initial_users["user2"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="view_snippet"),
        )

    def test_export_document_structure(self, client, snippet_with_relations):
        response = client.get(self.url)
        assert response.status_code == 200
        assert response["Content-Disposition"].startswith('attachment; filename="snypy-export-')

        document = response.json()
        assert document["format"] == "snypy-export"
        assert document["version"] == 1
        assert len(document["snippets"]) == 1
        assert document["snippets"][0]["title"] == "Sort dict by value"

    def test_export_excludes_foreign_snippets(self, client):
        Snippet.objects.create(user=self.user2, title="Foreign", visibility=Snippet.VISIBILITY_PRIVATE)
        response = client.get(self.url)
        assert response.status_code == 200
        assert response.json()["snippets"] == []

    def test_export_respects_filter(self, client, snippet_with_relations):
        Snippet.objects.create(user=self.user1, title="Unlabeled", visibility=Snippet.VISIBILITY_PRIVATE)
        label_pk = snippet_with_relations.labels.first().pk

        response = client.get(self.url, {"labels": label_pk})
        assert response.status_code == 200
        titles = [entry["title"] for entry in response.json()["snippets"]]
        assert titles == ["Sort dict by value"]

    def test_export_requires_view_permission(self, client, auth_user2):
        response = client.get(self.url)
        assert response.status_code == 403
