from django.contrib.auth import get_user_model
from drf_multitokenauth.models import MultiToken
from rest_framework.test import APITestCase

User = get_user_model()


class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()

        self.password = "you_cannot_read_this"
        self.user1 = User.objects.create_user("user1", "user1@test.com", self.password)
        self.user2 = User.objects.create_user("user2", "user2@test.com", self.password)
        self.user3 = User.objects.create_user("user3", "user3@test.com", self.password)
        self.user4 = User.objects.create_user("user4", "user4@test.com", self.password)

        self.token1 = MultiToken.objects.create(user=self.user1)
        self.token2 = MultiToken.objects.create(user=self.user2)
        self.token3 = MultiToken.objects.create(user=self.user3)
        self.token4 = MultiToken.objects.create(user=self.user4)

        self.api_authentication(self.token1)

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
