from concurrency.admin import ConcurrentModelAdmin
from demoproject.demoapp.models import DemoModel, proxy_factory


class DemoModelAdmin(ConcurrentModelAdmin):
    # list_display = [f.name for f in DemoModel._meta.fields]
    list_display = ('id', 'char', 'integer')
    list_display_links = ('id', )
    list_editable = ('char', 'integer')
    actions = None


try:
    from import_export.admin import ImportExportMixin

    class ImportExportDemoModelAdmin(ImportExportMixin, ConcurrentModelAdmin):
        # list_display = [f.name for f in DemoModel._meta.fields]
        list_display = ('id', 'char', 'integer')
        list_display_links = ('id', )
        list_editable = ('char', 'integer')
        actions = None

except:
    pass

def register(site):
    site.register(DemoModel, DemoModelAdmin)
    site.register(proxy_factory("ImportExport"), ImportExportDemoModelAdmin)
