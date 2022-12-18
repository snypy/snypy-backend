from django.db import models

from .managers import ContentPageManager


class ContentPage(models.Model):
    objects = ContentPageManager()

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, primary_key=True)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Content Page"
        verbose_name_plural = "Content Pages"
