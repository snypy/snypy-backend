from django.db.models import Count, Case, When, F, CharField

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
    filterset_class = UserTeamFilter

    def get_queryset(self):
        return self.queryset.viewable().annotate(
            snippet_count=Count(
                Case(
                    When(team__snippets__user=F("user"), then=1),
                    output_field=CharField(),
                )
            )
        )
