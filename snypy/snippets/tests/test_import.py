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


@pytest.mark.django_db
class TestSnippetImportEndpoint:
    url = reverse("snippet-import")

    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="add_snippet"),
            Permission.objects.get(codename="add_label"),
        )

    def test_import_creates_snippets(self, client):
        response = client.post(self.url, import_document(), format="json")
        assert response.status_code == 201
        assert response.json() == {"snippets_created": 1, "labels_created": 1, "languages_created": 1}
        assert Snippet.objects.get(title="Sort dict by value").user == self.user1

    def test_invalid_entry_imports_nothing(self, client):
        document = import_document()
        document["snippets"].append({"title": "x" * 300})

        response = client.post(self.url, document, format="json")
        assert response.status_code == 400
        assert "1" in response.json()["snippets"]
        assert Snippet.objects.count() == 0

    def test_import_into_team(self, client):
        team = Team.objects.create(name="Team Python")
        UserTeam.objects.filter(team=team).delete()
        UserTeam.objects.create(user=self.user1, team=team, role=UserTeam.ROLE_CONTRIBUTOR)

        response = client.post(self.url, import_document(team=team.pk), format="json")
        assert response.status_code == 201
        snippet = Snippet.objects.get(title="Sort dict by value")
        assert snippet.team == team
        assert snippet.labels.get().team == team

    def test_invalid_team_role_rejected(self, client, initial_users):
        team = Team.objects.create(name="Team Python")
        UserTeam.objects.filter(team=team).delete()
        UserTeam.objects.create(user=self.user1, team=team, role=UserTeam.ROLE_SUBSCRIBER)

        response = client.post(self.url, import_document(team=team.pk), format="json")
        assert response.status_code == 400
        assert Snippet.objects.count() == 0

    def test_requires_add_snippet_permission(self, client, auth_user2, initial_users):
        initial_users["user2"].user_permissions.add(
            Permission.objects.get(codename="add_label"),
        )

        response = client.post(self.url, import_document(), format="json")
        assert response.status_code == 403

    def test_requires_add_label_permission(self, client):
        self.user1.user_permissions.remove(
            Permission.objects.get(codename="add_label"),
        )

        response = client.post(self.url, import_document(), format="json")
        assert response.status_code == 403
        assert Snippet.objects.count() == 0

    def test_shared_label_and_language_counted_once(self, client):
        document = import_document()
        document["snippets"].append(
            {
                "title": "Second snippet",
                "description": "",
                "visibility": "PRIVATE",
                "labels": ["python"],
                "files": [{"name": "b.py", "language": "Python", "content": "print(2)"}],
            }
        )

        response = client.post(self.url, document, format="json")
        assert response.status_code == 201
        assert response.json() == {"snippets_created": 2, "labels_created": 1, "languages_created": 1}
        assert Label.objects.filter(name="python").count() == 1
        assert Language.objects.filter(name="Python").count() == 1

    def test_import_requires_authentication(self, client):
        client.credentials()
        response = client.post(self.url, import_document(), format="json")
        assert response.status_code == 401


@pytest.mark.django_db
class TestExportImportRoundTrip:
    export_url = reverse("snippet-export")
    import_url = reverse("snippet-import")

    def test_round_trip(self, client, initial_users):
        user1 = initial_users["user1"]
        user2 = initial_users["user2"]
        user1.user_permissions.add(Permission.objects.get(codename="view_snippet"))
        user2.user_permissions.add(
            Permission.objects.get(codename="add_snippet"),
            Permission.objects.get(codename="add_label"),
        )

        snippet = Snippet.objects.create(user=user1, title="Original", description="desc")
        language = Language.objects.create(name="Python")
        File.objects.create(snippet=snippet, language=language, name="a.py", content="print(1)")
        label = Label.objects.create(name="python", user=user1)
        SnippetLabel.objects.create(snippet=snippet, label=label)

        document = client.get(self.export_url).json()

        client.credentials(HTTP_AUTHORIZATION="Token " + initial_users["token2"].key)
        response = client.post(self.import_url, document, format="json")
        assert response.status_code == 201

        imported = Snippet.objects.filter(user=user2).get()
        assert imported.title == "Original"
        assert imported.description == "desc"
        assert list(imported.labels.values_list("name", flat=True)) == ["python"]
        file = imported.files.get()
        assert file.name == "a.py"
        assert file.content == "print(1)"
        assert file.language == language
