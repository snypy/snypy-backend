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


def save_import(document, user):
    """Validate and save an import document as the given user."""
    from snippets.rest.serializers import SnippetImportSerializer

    class FakeRequest:
        pass

    request = FakeRequest()
    request.user = user
    serializer = SnippetImportSerializer(data=document, context={"request": request})
    assert serializer.is_valid(), serializer.errors
    return serializer.save()


@pytest.mark.django_db
class TestSnippetImportSave:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]

    def test_creates_snippet_files_labels(self):
        result = save_import(import_document(), self.user1)

        assert result == {"snippets_created": 1, "labels_created": 1, "languages_created": 1}

        snippet = Snippet.objects.get(title="Sort dict by value")
        assert snippet.user == self.user1
        assert snippet.team is None
        assert snippet.visibility == Snippet.VISIBILITY_PRIVATE
        assert list(snippet.labels.values_list("name", flat=True)) == ["python"]

        file = snippet.files.get()
        assert file.name == "sort.py"
        assert file.language.name == "Python"
        assert file.content == "sorted(d, key=d.get)"

    def test_reuses_existing_label_in_personal_scope(self):
        existing = Label.objects.create(name="python", user=self.user1)

        result = save_import(import_document(), self.user1)

        assert result["labels_created"] == 0
        snippet = Snippet.objects.get(title="Sort dict by value")
        assert snippet.labels.get() == existing

    def test_does_not_reuse_foreign_personal_label(self, initial_users):
        Label.objects.create(name="python", user=initial_users["user2"])

        result = save_import(import_document(), self.user1)

        assert result["labels_created"] == 1
        assert Label.objects.filter(name="python").count() == 2

    def test_reuses_existing_language(self):
        Language.objects.create(name="Python")

        result = save_import(import_document(), self.user1)

        assert result["languages_created"] == 0
        assert Language.objects.filter(name="Python").count() == 1

    def test_team_scope_label_created_in_team(self):
        team = Team.objects.create(name="Team Python")

        document = import_document()
        # bypass validate_team (needs request middleware) — set validated team directly
        from snippets.rest.serializers import SnippetImportSerializer

        class FakeRequest:
            pass

        request = FakeRequest()
        request.user = self.user1
        serializer = SnippetImportSerializer(data=document, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        serializer.validated_data["team"] = team
        result = serializer.save()

        assert result["snippets_created"] == 1
        snippet = Snippet.objects.get(title="Sort dict by value")
        assert snippet.team == team
        label = snippet.labels.get()
        assert label.team == team

    def test_duplicate_language_rows_do_not_break_import(self):
        Language.objects.create(name="Python")
        Language.objects.create(name="Python")

        result = save_import(import_document(), self.user1)

        assert result["languages_created"] == 0
        assert Language.objects.filter(name="Python").count() == 2

    def test_duplicate_label_names_in_entry_link_once(self):
        document = import_document()
        document["snippets"][0]["labels"] = ["python", "python"]

        result = save_import(document, self.user1)

        assert result["labels_created"] == 1
        snippet = Snippet.objects.get(title="Sort dict by value")
        assert snippet.snippet_labels.count() == 1
