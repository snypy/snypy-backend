from django.contrib import admin

from .models import ContentPage


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title")
