from rest_framework import viewsets, filters


class BaseModelViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return self.queryset.viewable()
