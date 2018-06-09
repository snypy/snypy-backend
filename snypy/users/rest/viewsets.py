from django.contrib.auth import get_user_model

from core.rest.viewsets import BaseModelViewSet
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
