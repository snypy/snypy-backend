from core.models.managers import BaseManager

from .querysets import (
    ContentPageQuerySet,
)


ContentPageManager = BaseManager.from_queryset(ContentPageQuerySet)
