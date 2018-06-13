from core.rest.viewsets import BaseModelViewSet

from ..models import Team, UserTeam
from .filters import UserTeamFilter
from .serializers import TeamSerializer, UserTeamSerializer


class TeamViewSet(BaseModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class UserTeamViewSet(BaseModelViewSet):
    queryset = UserTeam.objects.all()
    serializer_class = UserTeamSerializer
    filter_class = UserTeamFilter
