from rest_framework import serializers
from apps.general.models import Notification


class NotificationSerializer(serializers.ModelSerializer):


    class Meta:
        model = Notification
        fields = ('message', 'status')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        return represent