import pytest

from core.apps import CoreConfig


@pytest.mark.django_db
def test_app_config():
    assert CoreConfig.name == "core"
