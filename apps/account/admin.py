from django.contrib import admin
from apps.account.models import Account, LoginHistory
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class AccountAdmin(ImportExportModelAdmin):
    readonly_fields = ['password']
    list_display = ['id', 'username', 'email', 'fullname', 'is_staff', 'is_active']
    fieldsets = (
        (_('Credentials'), {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email', 'fullname')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser', 'is_staff'].disabled = True
        return form


class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'id', 'date_time', 'ip', 'user_agent', 'is_logged_in']
    list_filter = ['user']


admin.site.register(Account, AccountAdmin)
admin.site.register(LoginHistory, LoginHistoryAdmin)
    
