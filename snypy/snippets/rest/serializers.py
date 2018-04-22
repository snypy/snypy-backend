from rest_framework.relations import PrimaryKeyRelatedField

from core.rest.serializers import BaseSerializer
from ..models import Snippet, File, Label, Language, SnippetLabel, Extension


class SnippetSerializer(BaseSerializer):
    class Meta:
        model = Snippet
        fields = ('pk', 'url', 'title', 'description', 'visibility', 'user', )


class FileSerializer(BaseSerializer):
    snippet = PrimaryKeyRelatedField(queryset=Snippet.objects.all())
    language = PrimaryKeyRelatedField(queryset=Language.objects.all())

    class Meta:
        model = File
        fields = ('pk', 'url', 'snippet', 'language', 'name', 'content', )


class LabelSerializer(BaseSerializer):
    snippets = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Label
        fields = ('pk', 'url', 'snippets', 'name', 'user', )


class LanguageSerializer(BaseSerializer):
    class Meta:
        model = Language
        fields = ('pk', 'url', 'name', )


class SnippetLabelSerializer(BaseSerializer):
    snippet = PrimaryKeyRelatedField(queryset=Snippet.objects.all())
    label = PrimaryKeyRelatedField(queryset=Label.objects.all())

    class Meta:
        model = SnippetLabel
        fields = ('pk', 'url', 'snippet', 'label', )


class ExtensionSerializer(BaseSerializer):
    language = PrimaryKeyRelatedField(queryset=Language.objects.all())

    class Meta:
        model = Extension
        fields = ('pk', 'url', 'name', 'language', )
