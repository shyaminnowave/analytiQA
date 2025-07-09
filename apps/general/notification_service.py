from django.contrib.contenttypes.models import ContentType
from .models import Notification

class NotificationService:

    @staticmethod
    def create_notification(recipient, owner, status, object_id, message, instance):
        notification_data = {
            'message': message,
            'user': owner,
            'object_id': object_id,
            'status': status,
            'content_type': ContentType.objects.get_for_model(instance),
            'assigned_to': recipient,
        }
        return Notification.objects.create(**notification_data)