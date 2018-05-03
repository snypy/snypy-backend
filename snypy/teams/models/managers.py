from core.models.managers import BaseManager

from .querysets import TeamQuerySet, UserTeamQuerySet


TeamManager = BaseManager.from_queryset(TeamQuerySet)
UserTeamManger = BaseManager.from_queryset(UserTeamQuerySet)
