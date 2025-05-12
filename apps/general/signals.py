from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.general.models import Notification
from django.core.cache import cache
from apps.general.apis.serializers import NotificationSerializer


@receiver(pre_save, sender=Notification)
def set_notification_cache(sender, instance, created, **kwargs):
    _data = NotificationSerializer(Notification.objects.filter(is_read=False), many=True).data
    cache.delete('notification_cache')
    return