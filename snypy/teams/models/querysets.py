from django_userforeignkey.request import get_current_user

from core.models.querysets import BaseQuerySet


class TeamQuerySet(BaseQuerySet):

    def viewable(self):
        user = get_current_user()
        return self.filter(user_teams__user=user).distinct()


class UserTeamQuerySet(BaseQuerySet):

    def viewable(self):
        user = get_current_user()
        return self.filter(team__user_teams__user=user).distinct()

    def editable(self):
        from teams.models import UserTeam

        user = get_current_user()
        return self.filter(
            team__user_teams__user=user,
            team__user_teams__role=UserTeam.ROLE_EDITOR
        ).distinct()
