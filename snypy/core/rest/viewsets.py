from django.contrib.auth.models import User
from rest_framework import viewsets, filters

from .serializers import UserSerializer


class BaseModelViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter,)

    # def get_queryset(self):
    #     if self.request.user.is_authenticated:
    #         return self.queryset.all()
    #     return self.queryset.none()


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
