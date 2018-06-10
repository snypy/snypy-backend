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

    favorite = django_filters.BooleanFilter(method='is_favorite', label="Is favorite?", )

    labeled = django_filters.BooleanFilter(method='is_labeled', label="Is labeled?", )

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

    def is_favorite(self, queryset, name, value):
        pass

    def is_labeled(self, queryset, name, value):
        if value:
            return queryset.exclude(labels=None)

        return queryset.filter(labels=None)


class LabelFilter(django_filters.FilterSet):

    class Meta:
        model = Label
        fields = [
            'user',
            'team',
        ]
