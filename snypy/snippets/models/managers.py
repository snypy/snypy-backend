from core.models.managers import BaseManager

from .querysets import (
    SnippetQuerySet,
    FileQuerySet,
    LabelQuerySet,
    LanguageQuerySet,
    ExtensionQuerySet,
    SnippetLabelQuerySet,
    SnippetFavoriteQuerySet,
)


SnippetManager = BaseManager.from_queryset(SnippetQuerySet)
FileManager = BaseManager.from_queryset(FileQuerySet)
LabelManager = BaseManager.from_queryset(LabelQuerySet)
LanguageManager = BaseManager.from_queryset(LanguageQuerySet)
ExtensionManager = BaseManager.from_queryset(ExtensionQuerySet)
SnippetLabelManager = BaseManager.from_queryset(SnippetLabelQuerySet)
SnippetFavoriteManager = BaseManager.from_queryset(SnippetFavoriteQuerySet)
