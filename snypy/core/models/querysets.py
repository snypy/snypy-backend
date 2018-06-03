from django.db import models


class BaseQuerySet(models.QuerySet):

    def viewable(self):
        return self.all()

    def editable(self):
        return self.viewable()

    def deletable(self):
        return self.editable()
