from core.utils.rest_router import router

from .rest.viewsets import UserViewSet


# Register rest views
router.register(r'user', UserViewSet)
