import django_filters

from snippets.models import File, Snippet, Label


class FileFilter(django_filters.FilterSet):

    class Meta:
        model = File
        fields = [
            'snippet',
            'language',
        ]


class SnippetFilter(django_filters.FilterSet):

    favorite = django_filters.BooleanFilter(method='filter_is_favorite', label="Is favorite?", )

    labeled = django_filters.BooleanFilter(method='filter_is_labeled', label="Is labeled?", )

    user = django_filters.NumberFilter(method='filter_user', label="User", )

    # ToDo: Add after shares app
    # shared_to = django_filters.NumberFilter(field_name="shared__user")
    # shared_from = django_filters.NumberFilter(field_name="shared__user")

    class Meta:
        model = Snippet
        fields = [
            'labels',
            'visibility',
            'files__language',
            'user',
            'team',
        ]

    def filter_is_favorite(self, queryset, name, value):
        pass

    def filter_is_labeled(self, queryset, name, value):
        if value:
            return queryset.exclude(labels=None)

        return queryset.filter(labels=None)

    def filter_user(self, queryset, name, value):
        return queryset.filter(
            user=value,
            team=None,
        )


class LabelFilter(django_filters.FilterSet):

    user = django_filters.NumberFilter(method='filter_user', label="User", )

    class Meta:
        model = Label
        fields = [
            'user',
            'team',
        ]

    def filter_user(self, queryset, name, value):
        return queryset.filter(
            user=value,
            team=None,
        )
