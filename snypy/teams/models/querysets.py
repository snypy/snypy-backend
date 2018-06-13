from django_userforeignkey.request import get_current_user

from core.models.querysets import BaseQuerySet


class TeamQuerySet(BaseQuerySet):

    def viewable(self):
        user = get_current_user()
        return self.filter(user_teams__user=user)


class UserTeamQuerySet(BaseQuerySet):
    pass
