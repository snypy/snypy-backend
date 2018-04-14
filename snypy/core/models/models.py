from __future__ import unicode_literals

from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True
