from django.contrib import admin
from apps.stb.models import Language, STBManufacture, NatCo, STBNode, STBNodeConfig,  \
    NatcoRelease, STBAuthToken, StbResult, StbAPIEndpoint, NatCoFirmware
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin
# Register your models here.


@admin.register(Language)
class LanguageAdmin(ImportExportModelAdmin):
     search_fields = ['language']


@admin.register(STBManufacture)
class STBManufactureAdmin(ImportExportModelAdmin):
    search_fields = ['manufacture']


@admin.register(NatCo)
class NatcoAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):

    list_display = ['natco', 'country']
    search_fields = ['language', 'manufacture']
    autocomplete_fields = ['language', 'manufacture']


@admin.register(NatcoRelease)
class NatcoReleaseAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ['id', 'natcos', 'version', 'android_version']



admin.site.register(STBNode, ImportExportModelAdmin)
admin.site.register(STBNodeConfig, ImportExportModelAdmin)
admin.site.register(NatCoFirmware)
admin.site.register(STBAuthToken)
admin.site.register(StbResult)
admin.site.register(StbAPIEndpoint)