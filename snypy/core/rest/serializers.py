from django.contrib.auth.models import User
from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):

    def get_queryset(self):
        return None


class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')
