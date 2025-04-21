from django.urls import path
from apps.stb.apis.views import LanguageListView, LanguageDetailView, StbManufactureListView, \
    StbManufactureDetailView, NatCoAPIView, NatCoOptionView, LanguageOptionView, \
    DeviceOptionView, NatCoDetailAPIView, NatcoInfoView

app_name = 'stb'

urlpatterns = [
    # Lists and Create endpoints
    path('language', LanguageListView.as_view(), name='language'),
    path('stb-manufacture', StbManufactureListView.as_view(), name='stb-manufacture'),
    path('natCo', NatCoAPIView.as_view(), name='natCo'),

    # Detail, Update, Delete endpoints
    path('language/<int:pk>', LanguageDetailView.as_view(), name='language-detail'),
    path('stb-manufacture/<int:pk>', StbManufactureDetailView.as_view(), name='stb-detail'),
    path('natCo/<int:pk>', NatCoDetailAPIView.as_view(), name="natCo-detail"),

    # NatcoRelease
    path('natCo-release', NatcoInfoView.as_view()),

    # Option API endpoints
    path('natCo-option', NatCoOptionView.as_view(), name='natCo-option'),
    path('language-option', LanguageOptionView.as_view(), name='language-option'),
    path('device-option', DeviceOptionView.as_view(), name='device-option')
]
