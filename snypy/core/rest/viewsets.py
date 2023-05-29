from rest_framework import viewsets

from core.rest.permissions import BaseModelPermissions


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [BaseModelPermissions]

    def get_queryset(self):
        return self.queryset.viewable()
