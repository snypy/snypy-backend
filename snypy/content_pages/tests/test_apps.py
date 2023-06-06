import pytest

from content_pages.apps import ContentPagesConfig


@pytest.mark.django_db
def test_app_config():
    assert ContentPagesConfig.name == "content_pages"
    assert ContentPagesConfig.default_auto_field == "django.db.models.BigAutoField"
