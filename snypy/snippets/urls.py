from core.utils.rest_router import router

from .rest.viewsets import (
    SnippetViewSet,
    FileViewSet,
    LabelViewSet,
    LanguageViewSet,
    SnippetLabelViewSet,
    ExtensionViewSet,
    SnippetFavoriteViewSet,
)


# Register rest views
router.register(r"snippet", SnippetViewSet)
router.register(r"file", FileViewSet)
router.register(r"label", LabelViewSet)
router.register(r"language", LanguageViewSet)
router.register(r"snippetlabel", SnippetLabelViewSet)
router.register(r"extension", ExtensionViewSet)
router.register(r"snippetfavorite", SnippetFavoriteViewSet)
