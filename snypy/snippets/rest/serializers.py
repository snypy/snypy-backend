from rest_framework import fields


from core.rest.serializers import BaseSerializer
from ..models import Snippet, File, Label, Language, SnippetLabel, Extension


class SnippetSerializer(BaseSerializer):
    class Meta:
        model = Snippet
        fields = ('pk', 'url', 'title', 'description', 'visibility', 'user', )


class FileSerializer(BaseSerializer):
    class Meta:
        model = File
        fields = ('pk', 'url', 'snippet', 'language', 'name', 'content', )


class LabelSerializer(BaseSerializer):
    class Meta:
        model = Label
        fields = ('pk', 'url', 'snippets', 'name', 'user', )


class LanguageSerializer(BaseSerializer):
    class Meta:
        model = Language
        fields = ('pk', 'url', 'name', )


class SnippetLabelSerializer(BaseSerializer):
    class Meta:
        model = SnippetLabel
        fields = ('pk', 'url', 'snippet', 'label', )


class ExtensionSerializer(BaseSerializer):
    class Meta:
        model = Extension
        fields = ('pk', 'url', 'name', 'language', )
