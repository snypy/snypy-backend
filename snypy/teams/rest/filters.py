import django_filters

from teams.models import UserTeam


class UserTeamFilter(django_filters.FilterSet):

    class Meta:
        model = UserTeam
        fields = [
            'user',
            'team',
        ]
