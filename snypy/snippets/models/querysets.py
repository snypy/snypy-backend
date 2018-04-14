from core.models.querysets import BaseQuerySet


class SnippetManager(BaseQuerySet):
    pass


class FileManager(BaseQuerySet):
    pass


class LabelManager(BaseQuerySet):
    pass


class LanguageManager(BaseQuerySet):
    pass


class ExtensionManager(BaseQuerySet):
    pass


class SnippetLabelManager(BaseQuerySet):
    pass
