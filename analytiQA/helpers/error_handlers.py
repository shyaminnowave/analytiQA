import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status


logger = logging.getLogger(__name__)


class Error404View(generics.GenericAPIView):

    def handle_exception(self, exc):
        return Response(
            {
                'status': False,
                'data': "No data",
                'message': "Invalid URL",
                'status_code': status.HTTP_404_NOT_FOUND
            },
            status=status.HTTP_404_NOT_FOUND
        )


class Error500View(generics.GenericAPIView):

    def handle_exception(self, exc):
        return Response(
            {
                'status': False,
                'data': "No data",
                'message': str(exc),
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


error404 = Error404View.as_view()
error500 = Error500View.as_view()


