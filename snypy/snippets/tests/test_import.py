import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from teams.models import Team, UserTeam
from snippets.models import Snippet, File, Label, Language, SnippetLabel


def import_document(**overrides):
    document = {
        "format": "snypy-export",
        "version": 1,
        "snippets": [
            {
                "title": "Sort dict by value",
                "description": "One-liner",
                "visibility": "PRIVATE",
                "labels": ["python"],
                "files": [{"name": "sort.py", "language": "Python", "content": "sorted(d, key=d.get)"}],
            }
        ],
    }
    document.update(overrides)
    return document


@pytest.mark.django_db
class TestSnippetImportSerializerValidation:
    def test_valid_document(self):
        from snippets.rest.serializers import SnippetImportSerializer

        serializer = SnippetImportSerializer(data=import_document())
        assert serializer.is_valid(), serializer.errors

    def test_rejects_wrong_format(self):
        from snippets.rest.serializers import SnippetImportSerializer

        serializer = SnippetImportSerializer(data=import_document(format="other"))
        assert not serializer.is_valid()
        assert "format" in serializer.errors

    def test_rejects_unknown_version(self):
        from snippets.rest.serializers import SnippetImportSerializer

        serializer = SnippetImportSerializer(data=import_document(version=2))
        assert not serializer.is_valid()
        assert "version" in serializer.errors

    def test_reports_errors_per_snippet_index(self):
        from snippets.rest.serializers import SnippetImportSerializer

        document = import_document()
        document["snippets"].append({"title": "x" * 300, "files": [], "labels": []})

        serializer = SnippetImportSerializer(data=document)
        assert not serializer.is_valid()
        assert 1 in serializer.errors["snippets"]
        assert 0 not in serializer.errors["snippets"]

    def test_rejects_file_without_language(self):
        from snippets.rest.serializers import SnippetImportSerializer

        document = import_document()
        document["snippets"][0]["files"][0].pop("language")

        serializer = SnippetImportSerializer(data=document)
        assert not serializer.is_valid()
