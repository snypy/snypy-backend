from django.contrib.auth import get_user_model
from django_gravatar.helpers import get_gravatar_url
from rest_framework.fields import SerializerMethodField

from core.rest.serializers import BaseSerializer

User = get_user_model()


class UserSerializer(BaseSerializer):
    avatar = SerializerMethodField()

    class Meta:
        model = User
        fields = ("pk", "url", "username", "email", "is_staff", "avatar")

    def get_avatar(self, obj):
        return obj.get_avatar(size=100)
