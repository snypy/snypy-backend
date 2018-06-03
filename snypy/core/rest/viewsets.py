from django.contrib.auth.models import User

from rest_framework import viewsets, filters

from .serializers import UserSerializer


class BaseModelViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return self.queryset.viewable()


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
