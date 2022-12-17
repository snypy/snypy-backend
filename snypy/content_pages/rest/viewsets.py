from core.rest.viewsets import BaseModelViewSet

from ..models import ContentPage
from .serializers import ContentPageSerializer


class ContentPageViewSet(BaseModelViewSet):
    queryset = ContentPage.objects.all()
    serializer_class = ContentPageSerializer
    search_fields = ("slug",)
    basename = "slug"
