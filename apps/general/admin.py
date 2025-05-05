from django.contrib import admin
from apps.general.models import Notification, StatusGroup, Status

# Register your models here.

@admin.register(StatusGroup)
class StatusGroupAdmin(admin.ModelAdmin):
    pass

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass
