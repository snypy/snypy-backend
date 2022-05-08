from django.db.models import Q
from django_userforeignkey.request import get_current_user

from core.models.querysets import BaseQuerySet


class SnippetQuerySet(BaseQuerySet):
    def _filter_by_roles(self, roles):
        from teams.models import UserTeam
        from snippets.models import Snippet

        user = get_current_user()

        if user.is_anonymous:
            return self.filter(visibility=Snippet.VISIBILITY_PUBLIC)

        return self.filter(
            Q(
                visibility=Snippet.VISIBILITY_PUBLIC,
            )
            | Q(
                user=user,
            )
            | Q(
                team__in=UserTeam.objects.filter(
                    user=user,
                    role__in=roles,
                ).values_list("team", flat=True)
            )
        )

    def viewable(self):
        from teams.models import UserTeam

        return self._filter_by_roles([UserTeam.ROLE_SUBSCRIBER, UserTeam.ROLE_CONTRIBUTOR, UserTeam.ROLE_EDITOR])

    def editable(self):
        from teams.models import UserTeam

        return self._filter_by_roles([UserTeam.ROLE_EDITOR])

    def deletable(self):
        from teams.models import UserTeam

        return self._filter_by_roles([UserTeam.ROLE_EDITOR])


class FileQuerySet(BaseQuerySet):
    def viewable(self):
        from snippets.models import Snippet

        return self.filter(snippet__in=Snippet.objects.viewable().values_list("pk", flat=True))

    def editable(self):
        from snippets.models import Snippet

        return self.filter(snippet__in=Snippet.objects.editable().values_list("pk", flat=True))


class LabelQuerySet(BaseQuerySet):
    def viewable(self):
        from teams.models import UserTeam

        user = get_current_user()

        return self.filter(
            Q(
                user=user,
            )
            | Q(team__in=UserTeam.objects.filter(user=user).values_list("team", flat=True))
        )


class LanguageQuerySet(BaseQuerySet):
    pass


class ExtensionQuerySet(BaseQuerySet):
    pass


class SnippetLabelQuerySet(BaseQuerySet):
    def viewable(self):
        from snippets.models import Snippet

        return self.filter(snippet__in=Snippet.objects.viewable().values_list("pk", flat=True))

    def editable(self):
        from snippets.models import Snippet

        return self.filter(snippet__in=Snippet.objects.editable().values_list("pk", flat=True))


class SnippetFavoriteQuerySet(BaseQuerySet):
    def viewable(self):
        user = get_current_user()
        return self.filter(user=user)

    def editable(self):
        return self.none()

    def deletable(self):
        return self.viewable()
