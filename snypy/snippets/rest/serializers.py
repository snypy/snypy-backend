from django.db import transaction

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.fields import SerializerMethodField, IntegerField

from core.rest.serializers import BaseSerializer
from teams.models import Team, get_current_user, UserTeam
from ..models import Snippet, File, Label, Language, SnippetLabel, Extension, SnippetFavorite


class SnippetFileSerializer(BaseSerializer):
    pk = IntegerField(read_only=False, required=False)
    language = PrimaryKeyRelatedField(queryset=Language.objects.all())

    class Meta:
        model = File
        fields = (
            "pk",
            "url",
            "language",
            "name",
            "content",
            "created_date",
            "modified_date",
        )


class SnippetSerializer(BaseSerializer):
    user_display = SerializerMethodField()
    user_avatar = SerializerMethodField()
    labels = PrimaryKeyRelatedField(many=True, read_only=False, queryset=Label.objects.all(), required=False)
    files = SnippetFileSerializer(File.objects.none(), many=True, required=False)
    favorite = SerializerMethodField()

    class Meta:
        model = Snippet
        fields = (
            "pk",
            "url",
            "title",
            "description",
            "visibility",
            "user",
            "user_display",
            "user_avatar",
            "created_date",
            "modified_date",
            "labels",
            "files",
            "team",
            "editable",
            "deletable",
            "favorite",
        )

    def get_favorite(self, obj):
        return obj.snippet_favorites.exists() > 0

    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username

    def get_user_avatar(self, obj):
        if obj.user:
            return obj.user.get_avatar(size=25)

    def save(self):
        # Extract nested fields
        labels = self.validated_data.pop("labels") if "labels" in self.validated_data else None
        files = self.validated_data.pop("files") if "files" in self.validated_data else None

        # Save instance
        instance = super(SnippetSerializer, self).save()

        # Save labels
        if labels is not None:
            self.instance.labels.clear()
            labels_to_add = []
            for label in labels:
                labels_to_add.append(SnippetLabel(label=label, snippet=self.instance))
            SnippetLabel.objects.bulk_create(labels_to_add)

        if files is not None:
            files_to_add = []
            files_to_update = []
            for file in files:
                if "pk" in file and file["pk"] is not None:
                    files_to_update.append(file)
                else:
                    file["snippet"] = instance
                    files_to_add.append(File(**file))

            # Delete old files
            instance.files.exclude(pk__in=[file["pk"] for file in files_to_update]).delete()

            # Add new files
            instance.files.bulk_create(files_to_add)

            # Update existing files
            for file in files_to_update:
                instance.files.filter(pk=file.pop("pk")).update(**file)

    def validate_team(self, team):
        if team is None:
            return

        if Team.objects.viewable().filter(pk=team.pk).exists():
            if UserTeam.objects.filter(
                team=team, user=get_current_user(), role__in=[UserTeam.ROLE_CONTRIBUTOR, UserTeam.ROLE_EDITOR]
            ).exists():
                return team

        raise serializers.ValidationError("You cannot add users to this team")


class FileSerializer(BaseSerializer):
    snippet = PrimaryKeyRelatedField(queryset=Snippet.objects.all())
    language = PrimaryKeyRelatedField(queryset=Language.objects.all())

    class Meta:
        model = File
        fields = (
            "pk",
            "url",
            "snippet",
            "language",
            "name",
            "content",
            "created_date",
            "modified_date",
        )


class LabelSerializer(BaseSerializer):
    snippet_count = IntegerField(read_only=True, required=False)

    class Meta:
        model = Label
        fields = (
            "pk",
            "url",
            "name",
            "user",
            "created_date",
            "modified_date",
            "team",
            "snippet_count",
        )

    def validate_team(self, team):
        if team is None:
            return

        if Team.objects.viewable().filter(pk=team.pk).exists():
            return team

        raise serializers.ValidationError("Please select a valid Team")


class LanguageSerializer(BaseSerializer):
    snippet_count = IntegerField(read_only=True, required=False)

    class Meta:
        model = Language
        fields = (
            "pk",
            "url",
            "name",
            "snippet_count",
        )


class SnippetLabelSerializer(BaseSerializer):
    snippet = PrimaryKeyRelatedField(queryset=Snippet.objects.all())
    label = PrimaryKeyRelatedField(queryset=Label.objects.all())

    class Meta:
        model = SnippetLabel
        fields = (
            "pk",
            "url",
            "snippet",
            "label",
        )


class ExtensionSerializer(BaseSerializer):
    language = PrimaryKeyRelatedField(queryset=Language.objects.all())

    class Meta:
        model = Extension
        fields = (
            "pk",
            "url",
            "name",
            "language",
        )


class SnippetFavoriteSerializer(BaseSerializer):
    snippet = PrimaryKeyRelatedField(queryset=Snippet.objects.all())

    class Meta:
        model = SnippetFavorite
        fields = (
            "pk",
            "url",
            "snippet",
        )

    def validate_snippet(self, snippet):
        if not Snippet.objects.viewable().filter(pk=snippet.pk).exists():
            raise serializers.ValidationError("Snippet not found.")
        return snippet


class SnippetFavoriteActionSerializer(BaseSerializer):
    class Meta:
        model = SnippetFavorite
        fields = (
            "pk",
            "url",
        )


class SnippetExportFileSerializer(BaseSerializer):
    language = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = File
        fields = (
            "name",
            "language",
            "content",
        )


class SnippetExportSerializer(BaseSerializer):
    labels = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)
    files = SnippetExportFileSerializer(many=True, read_only=True)

    class Meta:
        model = Snippet
        fields = (
            "title",
            "description",
            "visibility",
            "created_date",
            "modified_date",
            "labels",
            "files",
        )


class SnippetImportFileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    language = serializers.CharField(max_length=255)
    content = serializers.CharField(allow_blank=True, default="", trim_whitespace=False)


class IndexedErrorListSerializer(serializers.ListSerializer):
    """Reports child validation errors keyed by index, omitting valid entries.

    DRF's default ListSerializer reports errors as a positional list padded
    with empty dicts for valid entries (e.g. [{}, {"title": [...]}]), which
    makes it awkward to tell which indices actually failed. This translates
    that into only the failing indices, e.g. {1: {"title": [...]}}, while
    still delegating to DRF's own validation (allow_empty, min_length,
    max_length, run_child_validation, etc.).
    """

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            if isinstance(exc.detail, list):
                raise serializers.ValidationError({index: detail for index, detail in enumerate(exc.detail) if detail})
            raise


class SnippetImportEntrySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default="", trim_whitespace=False)
    visibility = serializers.ChoiceField(choices=Snippet.VISIBILITIES, default=Snippet.VISIBILITY_PRIVATE)
    labels = serializers.ListField(child=serializers.CharField(max_length=255), default=list)
    files = SnippetImportFileSerializer(many=True, default=list)

    class Meta:
        list_serializer_class = IndexedErrorListSerializer


class SnippetImportSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=["snypy-export"])
    version = serializers.IntegerField(min_value=1, max_value=1)
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), required=False, allow_null=True, default=None
    )
    snippets = SnippetImportEntrySerializer(many=True)

    def validate_team(self, team):
        # get_current_user() resolves the user from django-userforeignkey's
        # thread-local, populated by request middleware -- not from
        # serializer context. Serializer-level tests without a real request
        # cannot exercise this validation.
        if team is None:
            return None

        if Team.objects.viewable().filter(pk=team.pk).exists():
            if UserTeam.objects.filter(
                team=team,
                user=get_current_user(),
                role__in=[UserTeam.ROLE_CONTRIBUTOR, UserTeam.ROLE_EDITOR],
            ).exists():
                return team

        raise serializers.ValidationError("Please select a valid Team")

    def save(self, **kwargs):
        user = self.context["request"].user
        team = self.validated_data["team"]
        entries = self.validated_data["snippets"]

        if team is not None:
            label_scope_filter = {"team": team}
        else:
            label_scope_filter = {"user": user, "team": None}

        labels_created = 0
        languages_created = 0
        label_cache = {}
        language_cache = {}

        with transaction.atomic():
            for entry in entries:
                snippet = Snippet.objects.create(
                    user=user,
                    team=team,
                    title=entry["title"],
                    description=entry["description"],
                    visibility=entry["visibility"],
                )

                for label_name in dict.fromkeys(entry["labels"]):
                    label = label_cache.get(label_name)
                    if label is None:
                        label = Label.objects.filter(name=label_name, **label_scope_filter).first()
                        if label is None:
                            label = Label.objects.create(name=label_name, user=user, team=team)
                            labels_created += 1
                        label_cache[label_name] = label
                    SnippetLabel.objects.create(snippet=snippet, label=label)

                for file_entry in entry["files"]:
                    language = language_cache.get(file_entry["language"])
                    if language is None:
                        language = Language.objects.filter(name=file_entry["language"]).first()
                        if language is None:
                            language = Language.objects.create(name=file_entry["language"])
                            languages_created += 1
                        language_cache[file_entry["language"]] = language
                    File.objects.create(
                        snippet=snippet,
                        language=language,
                        name=file_entry["name"],
                        content=file_entry["content"],
                    )

        return {
            "snippets_created": len(entries),
            "labels_created": labels_created,
            "languages_created": languages_created,
        }
