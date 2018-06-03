from django.db.models import Q
from django_userforeignkey.request import get_current_user

from core.models.querysets import BaseQuerySet


class SnippetQuerySet(BaseQuerySet):

    def viewable(self):
        from teams.models import UserTeam
        user = get_current_user()

        return self.filter(
            Q(
                user=user,
            ) | Q(
                team__in=UserTeam.objects.filter(user=user).values_list('team', flat=True)
            )
        )

    def editable(self):
        from teams.models import UserTeam
        user = get_current_user()

        return self.filter(
            Q(
                user=user,
            ) | Q(
                team__in=UserTeam.objects.filter(
                    user=user,
                    role__in=[UserTeam.ROLE_CONTRIBUTOR, UserTeam.ROLE_EDITOR],
                ).values_list('team', flat=True)
            )
        )


class FileQuerySet(BaseQuerySet):

    def viewable(self):
        from snippets.models import Snippet

        return self.filter(
            snippet__in=Snippet.objects.viewable().values_list('pk', flat=True)
        )

    def editable(self):
        from snippets.models import Snippet

        return self.filter(
            snippet__in=Snippet.objects.editable().values_list('pk', flat=True)
        )


class LabelQuerySet(BaseQuerySet):

    def viewable(self):
        from teams.models import UserTeam
        user = get_current_user()

        return self.filter(
            Q(
                user=user,
            ) | Q(
                team__in=UserTeam.objects.filter(user=user).values_list('team', flat=True)
            )
        )


class LanguageQuerySet(BaseQuerySet):
    pass


class ExtensionQuerySet(BaseQuerySet):
    pass


class SnippetLabelQuerySet(BaseQuerySet):

    def viewable(self):
        from snippets.models import Snippet

        return self.filter(
            snippet__in=Snippet.objects.viewable().values_list('pk', flat=True)
        )

    def editable(self):
        from snippets.models import Snippet

        return self.filter(
            snippet__in=Snippet.objects.editable().values_list('pk', flat=True)
        )