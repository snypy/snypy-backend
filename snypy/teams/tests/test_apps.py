import pytest

from teams.apps import TeamsConfig


@pytest.mark.django_db
def test_app_config():
    assert TeamsConfig.name == "teams"
