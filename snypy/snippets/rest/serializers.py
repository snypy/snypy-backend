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
        )

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
