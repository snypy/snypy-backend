from django.contrib.auth.models import AbstractUser

from .managers import UserManager


class User(AbstractUser):

    objects = UserManager()
