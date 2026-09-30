import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from snippets.models import File, Language, Snippet


@pytest.mark.django_db
class TestFileDescription:
    @pytest.fixture(autouse=True)
    def _setup(self, initial_users):
        self.user1 = initial_users["user1"]
        self.user1.user_permissions.add(
            Permission.objects.get(codename="add_snippet"),
            Permission.objects.get(codename="change_snippet"),
            Permission.objects.get(codename="add_file"),
            Permission.objects.get(codename="change_file"),
        )
        self.python = Language.objects.create(name="Python")

    def create_snippet(self, client, files):
        response = client.post(
            reverse("snippet-list"),
            {"title": "Python snippet", "files": files},
            format="json",
        )
        assert response.status_code == 201
        return response

    def test_create_snippet_with_file_descriptions(self, client):
        response = self.create_snippet(
            client,
            [
                {"language": self.python.pk, "name": "a.py", "content": "a = 1", "description": "# File A"},
                {"language": self.python.pk, "name": "b.py", "content": "b = 2", "description": "*File B*"},
            ],
        )

        descriptions = {file["name"]: file["description"] for file in response.data["files"]}
        assert descriptions == {"a.py": "# File A", "b.py": "*File B*"}

        snippet = Snippet.objects.get(pk=response.data["pk"])
        assert snippet.files.get(name="a.py").description == "# File A"
        assert snippet.files.get(name="b.py").description == "*File B*"

    def test_create_snippet_without_file_description(self, client):
        response = self.create_snippet(client, [{"language": self.python.pk, "name": "a.py", "content": "a = 1"}])

        assert response.data["files"][0]["description"] == ""
        assert File.objects.get(pk=response.data["files"][0]["pk"]).description == ""

    def test_update_file_description_through_snippet(self, client):
        response = self.create_snippet(
            client,
            [
                {"language": self.python.pk, "name": "a.py", "content": "a = 1", "description": "Old A"},
                {"language": self.python.pk, "name": "b.py", "content": "b = 2", "description": "Old B"},
            ],
        )
        files = {file["name"]: file for file in response.data["files"]}

        response = client.patch(
            reverse("snippet-detail", kwargs={"pk": response.data["pk"]}),
            {
                "files": [
                    {
                        "pk": files["a.py"]["pk"],
                        "language": self.python.pk,
                        "name": "a.py",
                        "content": "a = 1",
                        "description": "New **A**",
                    },
                    {
                        "pk": files["b.py"]["pk"],
                        "language": self.python.pk,
                        "name": "b.py",
                        "content": "b = 2",
                    },
                ]
            },
            format="json",
        )
        assert response.status_code == 200

        assert File.objects.get(pk=files["a.py"]["pk"]).description == "New **A**"
        # Omitting the description on update leaves the stored value untouched
        assert File.objects.get(pk=files["b.py"]["pk"]).description == "Old B"

    def test_read_description_via_file_endpoint(self, client):
        response = self.create_snippet(
            client,
            [{"language": self.python.pk, "name": "a.py", "content": "a = 1", "description": "## Usage"}],
        )
        file_pk = response.data["files"][0]["pk"]

        response = client.get(reverse("file-detail", kwargs={"pk": file_pk}))
        assert response.status_code == 200
        assert response.data["description"] == "## Usage"

    def test_write_description_via_file_endpoint(self, client):
        snippet = Snippet.objects.create(user=self.user1, title="Python snippet")

        response = client.post(
            reverse("file-list"),
            {"snippet": snippet.pk, "language": self.python.pk, "name": "a.py", "content": "a = 1"},
        )
        assert response.status_code == 201
        assert response.data["description"] == ""

        response = client.patch(
            reverse("file-detail", kwargs={"pk": response.data["pk"]}),
            {"description": "Some *markdown*"},
        )
        assert response.status_code == 200
        assert response.data["description"] == "Some *markdown*"
        assert File.objects.get(pk=response.data["pk"]).description == "Some *markdown*"
