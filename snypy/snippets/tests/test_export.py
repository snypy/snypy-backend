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
