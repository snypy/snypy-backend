from django.db import models
from django.utils.encoding import force_str

from django_userforeignkey.models.fields import UserForeignKey

from core.models import BaseModel, DateModelMixin
from .managers import (
    SnippetManager,
    FileManager,
    LabelManager,
    LanguageManager,
    ExtensionManager,
    SnippetLabelManager,
    SnippetFavoriteManager,
)


class Snippet(BaseModel, DateModelMixin):

    objects = SnippetManager()

    VISIBILITY_PUBLIC = "PUBLIC"
    VISIBILITY_PRIVATE = "PRIVATE"

    VISIBILITIES = (
        (VISIBILITY_PUBLIC, "Public"),
        (VISIBILITY_PRIVATE, "Private"),
    )

    user = UserForeignKey(
        auto_user_add=True,
        verbose_name="User",
        related_name="snippets",
        editable=False,
        on_delete=models.CASCADE,
    )

    team = models.ForeignKey(
        "teams.Team",
        related_name="snippets",
        verbose_name="Team",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    title = models.CharField(
        verbose_name="Title",
        max_length=255,
        null=False,
        blank=False,
    )

    description = models.TextField(
        verbose_name="Description",
        null=False,
        blank=True,
    )

    visibility = models.CharField(
        max_length=31,
        choices=VISIBILITIES,
        default=VISIBILITY_PRIVATE,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.title


class File(BaseModel, DateModelMixin):

    objects = FileManager()

    snippet = models.ForeignKey(
        "Snippet",
        related_name="files",
        verbose_name="Snippet",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    language = models.ForeignKey(
        "Language",
        related_name="files",
        verbose_name="Language",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    name = models.CharField(
        verbose_name="Name",
        max_length=255,
        null=False,
        blank=False,
    )

    content = models.TextField(
        verbose_name="Content",
        null=False,
        blank=True,
    )

    def __str__(self):
        return self.name


class Label(BaseModel, DateModelMixin):

    objects = LabelManager()

    snippets = models.ManyToManyField(
        "Snippet",
        related_name="labels",
        verbose_name="Snippets",
        through="SnippetLabel",
        through_fields=(
            "label",
            "snippet",
        ),
    )

    user = UserForeignKey(
        auto_user_add=True,
        verbose_name="User",
        related_name="labels",
        editable=False,
        on_delete=models.CASCADE,
    )

    team = models.ForeignKey(
        "teams.Team",
        related_name="labels",
        verbose_name="Team",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    name = models.CharField(
        verbose_name="Name",
        max_length=255,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name


class Language(BaseModel):

    objects = LanguageManager()

    name = models.CharField(
        verbose_name="Name",
        max_length=255,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name


class Extension(BaseModel):

    objects = ExtensionManager()

    language = models.ForeignKey(
        "Language",
        related_name="extensions",
        verbose_name="Language",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    name = models.CharField(
        verbose_name="Name",
        max_length=31,
        null=False,
        blank=False,
        unique=True,
    )

    def __str__(self):
        return self.name


class SnippetLabel(BaseModel):

    objects = SnippetLabelManager()

    snippet = models.ForeignKey(
        "Snippet",
        related_name="snippet_labels",
        verbose_name="Snippet",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    label = models.ForeignKey(
        "Label",
        related_name="snippet_labels",
        verbose_name="Label",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{force_str(self.snippet)} - {force_str(self.label)}"


class SnippetFavorite(BaseModel):

    objects = SnippetFavoriteManager()

    snippet = models.ForeignKey(
        "Snippet",
        related_name="snippet_favorites",
        verbose_name="Snippet",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    user = UserForeignKey(
        auto_user_add=True,
        related_name="snippet_favorites",
        verbose_name="User",
        editable=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{force_str(self.snippet)} - {force_str(self.user)}"
