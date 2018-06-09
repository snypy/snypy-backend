from django.contrib.auth import get_user_model

from core.rest.serializers import BaseSerializer

User = get_user_model()


class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')
