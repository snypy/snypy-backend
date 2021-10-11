from django.contrib import admin


from .models import Snippet, File, Label, Language, SnippetLabel, Extension, SnippetFavorite


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
    list_per_page = 5

    def get_list_per_page(self, request):
        request.GET = request.GET.copy()
        request_list_per_page = int(request.GET.pop('list_per_page', [0])[0])
        if request_list_per_page:
            return request_list_per_page

        return self.list_per_page

    def get_changelist_instance(self, request):
        """
        Return a `ChangeList` instance based on `request`. May raise
        `IncorrectLookupParameters`.
        """
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        # Add the action checkboxes if any actions are available.
        if self.get_actions(request):
            list_display = ['action_checkbox', *list_display]
        sortable_by = self.get_sortable_by(request)
        ChangeList = self.get_changelist(request)

        list_per_page = self.get_list_per_page(request)

        return ChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            self.get_list_filter(request),
            self.date_hierarchy,
            self.get_search_fields(request),
            self.get_list_select_related(request),
            list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            sortable_by,
        )


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


@admin.register(SnippetFavorite)
class SnippetFavoriteAdmin(admin.ModelAdmin):
    pass
