from rest_framework.relations import PrimaryKeyRelatedField

from core.rest.serializers import BaseSerializer
from ..models import Team, UserTeam


class TeamSerializer(BaseSerializer):

    class Meta:
        model = Team
        fields = (
            'pk',
            'url',
            'users',
            'name',
            'created_date',
            'modified_date',
        )


class UserTeamSerializer(BaseSerializer):

    class Meta:
        model = UserTeam
        fields = (
            'pk',
            'url',
            'user',
            'team',
            'created_date',
            'modified_date',
        )
