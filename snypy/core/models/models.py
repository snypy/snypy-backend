from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    @property
    def editable(self):
        return self.__class__.objects.filter(pk=self.pk).editable().exists()

    @property
    def deletable(self):
        return self.__class__.objects.filter(pk=self.pk).deletable().exists()


class DateModelMixin(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
