import pytest

from snippets.apps import SnippetsConfig


@pytest.mark.django_db
def test_app_config():
    assert SnippetsConfig.name == "snippets"
