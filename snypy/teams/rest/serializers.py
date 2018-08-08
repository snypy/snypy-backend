from rest_framework.fields import SerializerMethodField, IntegerField

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
    user_display = SerializerMethodField()
    snippet_count = IntegerField(read_only=True, required=False)

    class Meta:
        model = UserTeam
        fields = (
            'pk',
            'url',
            'user',
            'team',
            'created_date',
            'modified_date',
            'user_display',
            'snippet_count',
        )

    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username
