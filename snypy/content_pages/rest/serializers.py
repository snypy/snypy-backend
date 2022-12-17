from core.rest.serializers import BaseSerializer

from ..models import ContentPage


class ContentPageSerializer(BaseSerializer):
    class Meta:
        model = ContentPage
        fields = (
            "slug",
            "url",
            "title",
            "content",
        )
