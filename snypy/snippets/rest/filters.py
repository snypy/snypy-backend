import django_filters
from snippets.models import File


class FileFilter(django_filters.FilterSet):

    class Meta:
        model = File
        fields = ['snippet', 'language', ]
