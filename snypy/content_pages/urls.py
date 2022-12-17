from core.utils.rest_router import router

from .rest.viewsets import ContentPageViewSet


# Register rest views
router.register(r"contentpage", ContentPageViewSet)
