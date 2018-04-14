from django.db import models

from core.models import BaseModel
from .managers import SnippetManager, FileManager, LabelManager, LanguageManager, ExtensionManager, SnippetLabelManager


class Snippet(BaseModel):

    objects = SnippetManager()

    VISIBILITY_PUBLIC = 'PUBLIC'
    VISIBILITY_PRIVATE = 'PRIVATE'

    VISIBILITIEWS = (
        (VISIBILITY_PUBLIC, 'Public'),
        (VISIBILITY_PRIVATE, 'Private'),
    )
    
    title = models.CharField(
        verbose_name='Title',
        max_length=255,
        null=False,
        blank=False,
    )

    description = models.TextField(
        verbose_name='Description',
        null=False,
        blank=True,
    )

    visibility = models.CharField(
        max_length=31,
        choices=VISIBILITIEWS,
        default=VISIBILITY_PRIVATE,
        null=False,
        blank=False,
    )


class File(BaseModel):

    objects = FileManager()

    snippet = models.ForeignKey(
        'Snippet',
        related_name='files',
        verbose_name='Snippet',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    language = models.ForeignKey(
        'Language',
        related_name='language',
        verbose_name='Language',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    
    name = models.CharField(
        verbose_name='Name',
        max_length=255,
        null=False,
        blank=False,
    )

    content = models.TextField(
        verbose_name='Content',
        null=False,
        blank=True,
    )


class Label(BaseModel):

    objects = LabelManager()

    snippets = models.ManyToManyField(
        'Snippet',
        related_name='labels',
        verbose_name='Snippets',
        through='SnippetLabel',
        through_fields=('label', 'snippet', ),
    )

    name = models.CharField(
        verbose_name='Name',
        max_length=255,
        null=False,
        blank=False,
    )


class Language(BaseModel):

    objects = LanguageManager()

    name = models.CharField(
        verbose_name='Name',
        max_length=255,
        null=False,
        blank=False,
    )


class Extension(BaseModel):

    objects = ExtensionManager()

    language = models.ForeignKey(
        'Language',
        related_name='extensions',
        verbose_name='Language',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    name = models.CharField(
        verbose_name='Name',
        max_length=31,
        null=False,
        blank=False,
        unique=True,
    )


class SnippetLabel(BaseModel):

    objects = SnippetLabelManager()

    snippet = models.ForeignKey(
        'Snippet',
        related_name='snippet_labels',
        verbose_name='Snippet',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    label = models.ForeignKey(
        'Label',
        related_name='snippet_labels',
        verbose_name='Label',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
