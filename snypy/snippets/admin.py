from django.contrib import admin


from .models import Snippet, File, Label, Language, SnippetLabel, Extension


class SnippetLabelInline(admin.TabularInline):
    model = SnippetLabel
    extra = 1


class FileInline(admin.StackedInline):
    model = File
    extra = 1


class ExtensionInline(admin.StackedInline):
    model = Extension
    extra = 1


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    inlines = [
        SnippetLabelInline,
        FileInline,
    ]


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    pass


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    inlines = [
        ExtensionInline,
    ]


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    pass


@admin.register(SnippetLabel)
class SnippetLabelAdmin(admin.ModelAdmin):
    pass
