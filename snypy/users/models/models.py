from django.contrib.auth.models import AbstractUser
from django_gravatar.helpers import get_gravatar_url, has_gravatar

from .managers import UserManager


class User(AbstractUser):

    objects = UserManager()

    def get_avatar(self, size=25):
        # TODO: Add caching in future if rate limits are reached
        if has_gravatar(self.email):
            return get_gravatar_url(self.email, size=size)
        return f"https://www.gravatar.com/avatar/00000000000000000000000000000000?d=identicon&s={size}&f=y;'"
