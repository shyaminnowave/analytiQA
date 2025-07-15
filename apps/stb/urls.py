from django.urls import path
from .views import STBView

urlpatterns = [
    path('t', STBView.as_view(), name='stb-view'),
]