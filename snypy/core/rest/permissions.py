from rest_framework.permissions import DjangoModelPermissions


class BaseModelPermissions(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def has_object_permission(self, request, view, obj):
        has_permission = super().has_permission(request, view)

        if has_permission and view.action == "retrieve":
            return self._queryset(view).viewable().filter(pk=obj.pk).exists()

        if has_permission and view.action == "update":
            return self._queryset(view).editable().filter(pk=obj.pk).exists()

        if has_permission and view.action == "partial_update":
            return self._queryset(view).editable().filter(pk=obj.pk).exists()

        if has_permission and view.action == "destroy":
            return self._queryset(view).deletable().filter(pk=obj.pk).exists()

        return False
