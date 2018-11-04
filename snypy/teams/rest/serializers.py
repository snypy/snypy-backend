from django_userforeignkey.request import get_current_user
from rest_framework import serializers
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
            'role',
            'created_date',
            'modified_date',
            'user_display',
            'snippet_count',
        )

    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username

    def validate_team(self, team):
        if self.instance:
            if team != self.instance.team:
                raise serializers.ValidationError("Team cannot be changed")

        if Team.objects.viewable().filter(pk=team.pk).exists():
            if UserTeam.objects.filter(
                    team=team,
                    user=get_current_user(),
                    role__in=[UserTeam.ROLE_EDITOR]
            ).exists():
                return team

        raise serializers.ValidationError("Please select a valid Team")

    def validate_user(self, user):
        if self.instance:
            if user != self.instance.user:
                raise serializers.ValidationError("User cannot be changed")

        return user
