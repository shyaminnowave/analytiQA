from pyxlsb import open_workbook
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from apps.general.apis.serializers import NotificationSerializer
from apps.general.models import Notification
from rest_framework.views import Response
from rest_framework import status
from apps.core.apis.serializers import ExcelUploadSerializer
from django.core.cache import cache


class NotificationView(APIView):

    authentication_classes = (JWTAuthentication, SessionAuthentication)

    def get_queryset(self):
        queryset = Notification.objects.select_related('user').filter(assigned_to__email=self.request.user, is_read=False)
        return queryset


    def get(self, request, *args, **kwargs):
        if request.GET.get("action") == 'clear':
            self.get_queryset().update(is_read=True)
            cache.clear()

        cache_data = cache.get(f'{request.user}_notification_cache')
        print(cache_data if cache_data else None)
        if cache_data:
            return Response({
                "data": cache_data,
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "success",
                "count": len(cache_data)
            }, status=status.HTTP_200_OK)
        serializer = NotificationSerializer(self.get_queryset(), many=True)
        cache.set(f'{request.user}_notification_cache', serializer.data, timeout=60 * 15)
        response_format = {
            "data": serializer.data,
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "success",
            "count": len(serializer.data)
        }
        return Response(response_format, status=status.HTTP_200_OK)