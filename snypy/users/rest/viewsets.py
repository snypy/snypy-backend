from django.contrib.auth import get_user_model
from rest_framework.decorators import action

from rest_framework.response import Response

from core.rest.viewsets import BaseModelViewSet
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False)
    def current(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
