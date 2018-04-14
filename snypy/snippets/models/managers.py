from core.models.managers import BaseManager

from .querysets import SnippetManager, FileManager, LabelManager, LanguageManager, ExtensionManager, SnippetLabelManager


SnippetManager = BaseManager.from_queryset(SnippetManager)
FileManager = BaseManager.from_queryset(FileManager)
LabelManager = BaseManager.from_queryset(LabelManager)
LanguageManager = BaseManager.from_queryset(LanguageManager)
ExtensionManager = BaseManager.from_queryset(ExtensionManager)
SnippetLabelManager = BaseManager.from_queryset(SnippetLabelManager)
