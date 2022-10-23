import pytest
from django.contrib.auth import get_user_model
from drf_multitokenauth.models import MultiToken
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def client():
    yield APIClient()


@pytest.fixture(autouse=True)
def initial_users():
    password = "you_cannot_read_this"
    user1 = User.objects.create_user("user1", "user1@test.com", password)
    user2 = User.objects.create_user("user2", "user2@test.com", password)
    user3 = User.objects.create_user("user3", "user3@test.com", password)
    user4 = User.objects.create_user("user4", "user4@test.com", password)

    token1 = MultiToken.objects.create(user=user1)
    token2 = MultiToken.objects.create(user=user2)
    token3 = MultiToken.objects.create(user=user3)
    token4 = MultiToken.objects.create(user=user4)

    yield {
        "user1": user1,
        "user2": user2,
        "user3": user3,
        "user4": user4,
        "token1": token1,
        "token2": token2,
        "token3": token3,
        "token4": token4,
    }


@pytest.fixture(autouse=True)
def auth_user1(client, initial_users):
    client.credentials(HTTP_AUTHORIZATION="Token " + initial_users["token1"].key)


@pytest.fixture
def auth_user2(client, initial_users):
    client.credentials(HTTP_AUTHORIZATION="Token " + initial_users["token2"].key)
