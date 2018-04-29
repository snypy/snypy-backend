from core.rest.viewsets import BaseModelViewSet
from snippets.rest.filters import FileFilter, SnippetFilter
from ..models import Snippet, File, Label, Language, SnippetLabel, Extension
from .serializers import SnippetSerializer, FileSerializer, LabelSerializer, LanguageSerializer, \
    SnippetLabelSerializer, ExtensionSerializer


class SnippetViewSet(BaseModelViewSet):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    search_fields = ('title', 'description', )
    filter_class = SnippetFilter


class FileViewSet(BaseModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    search_fields = ('name', )
    filter_class = FileFilter


class LabelViewSet(BaseModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    search_fields = ('name', )


class LanguageViewSet(BaseModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    search_fields = ('name', )


class SnippetLabelViewSet(BaseModelViewSet):
    queryset = SnippetLabel.objects.all()
    serializer_class = SnippetLabelSerializer


class ExtensionViewSet(BaseModelViewSet):
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer
    search_fields = ('name', )
