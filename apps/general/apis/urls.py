from django.urls import path
from apps.general.apis.views import NotificationView

urlpatterns = [
    path('notification', NotificationView.as_view(), name='user-notification'),
]
