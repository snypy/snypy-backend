from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters

from .serializers import UserSerializer

User = get_user_model()


class BaseModelViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return self.queryset.viewable()


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
