from core.utils.rest_router import router

from .rest.viewsets import TeamViewSet, UserTeamViewSet


# Register rest views
router.register(r'team', TeamViewSet)
router.register(r'userteam', UserTeamViewSet)
