from rest_framework import fields


from core.rest.serializers import BaseSerializer
from ..models import Snippet, File, Label, Language, SnippetLabel, Extension


class SnippetSerializer(BaseSerializer):
    class Meta:
        model = Snippet
        fields = ('url', 'title', 'description', 'visibility', )


class FileSerializer(BaseSerializer):
    class Meta:
        model = File
        fields = ('url', 'snippet', 'language', 'name', 'content', )


class LabelSerializer(BaseSerializer):
    class Meta:
        model = Label
        fields = ('url', 'snippets', 'name', )


class LanguageSerializer(BaseSerializer):
    class Meta:
        model = Language
        fields = ('url', 'name', )


class SnippetLabelSerializer(BaseSerializer):
    class Meta:
        model = SnippetLabel
        fields = ('url', 'snippet', 'label', )


class ExtensionSerializer(BaseSerializer):
    class Meta:
        model = Extension
        fields = ('url', 'name', 'language', )
