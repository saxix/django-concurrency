from import_export.admin import ImportExportMixin
from concurrency.admin import ConcurrentModelAdmin


class DemoModelAdmin(ImportExportMixin, ConcurrentModelAdmin):
    # list_display = [f.name for f in DemoModel._meta.fields]
    list_display = ('id', 'char', 'integer')
    list_display_links = ('id', )
    list_editable = ('char', 'integer')
    actions = None
