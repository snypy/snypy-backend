from django.db.models import Count, OuterRef, Subquery

from core.rest.viewsets import BaseModelViewSet
from snippets.models import Snippet

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

    def get_queryset(self):
        viewable_snippets = Snippet.objects.viewable().filter(
            team=OuterRef('team'),
            user=OuterRef('user'),
        ).values('pk')

        return self.queryset.viewable().annotate(
            snippet_count=Count(
                Subquery(viewable_snippets)
            )
        )
