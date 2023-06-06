import pytest

from users.apps import UsersConfig


@pytest.mark.django_db
def test_app_config():
    assert UsersConfig.name == "users"
