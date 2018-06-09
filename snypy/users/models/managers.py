from django.contrib.auth.models import UserManager as DjangoUserManager

from core.models.managers import BaseManager
from .querysets import UserQuerySet


class UserManager(BaseManager.from_queryset(UserQuerySet), DjangoUserManager):
    pass
