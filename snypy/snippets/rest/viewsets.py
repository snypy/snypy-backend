from django.db.models import Count, CharField, When, Case, Q

from core.rest.viewsets import BaseModelViewSet
from teams.models import Team, get_user_model

from ..models import Snippet, File, Label, Language, SnippetLabel, Extension, SnippetFavorite
from .filters import FileFilter, SnippetFilter, LabelFilter, SnippetLabelFilter
from .serializers import SnippetSerializer, FileSerializer, LabelSerializer, LanguageSerializer, \
    SnippetLabelSerializer, ExtensionSerializer, SnippetFavoriteSerializer

User = get_user_model()


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
    filter_class = LabelFilter

    def get_queryset(self):
        viewable_snippets = Snippet.objects.viewable().values_list('pk', flat=True)

        return self.queryset.viewable().annotate(
            snippet_count=Count(
                Case(
                    When(snippets__in=viewable_snippets, then=1),
                    output_field=CharField(),
                )
            )
        )


class LanguageViewSet(BaseModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    search_fields = ('name', )

    def get_queryset(self):
        viewable_snippets = Snippet.objects.viewable().values_list('pk', flat=True)

        query = Q(files__snippet__in=viewable_snippets)

        if 'team' in self.request.query_params:
            team = Team.objects.get(pk=self.request.query_params['team'])
            query &= Q(files__snippet__team=team)

        if 'user' in self.request.query_params:
            user = User.objects.get(pk=self.request.query_params['user'])
            query &= Q(
                files__snippet__user=user,
                files__snippet__team=None,
            )

        return self.queryset.viewable().annotate(
            snippet_count=Count(
                Case(
                    When(query, then=1),
                    output_field=CharField(),
                )
            )
        )


class SnippetLabelViewSet(BaseModelViewSet):
    queryset = SnippetLabel.objects.all()
    serializer_class = SnippetLabelSerializer
    filter_class = SnippetLabelFilter


class ExtensionViewSet(BaseModelViewSet):
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer
    search_fields = ('name', )


class SnippetFavoriteViewSet(BaseModelViewSet):
    queryset = SnippetFavorite.objects.all()
    serializer_class = SnippetFavoriteSerializer
