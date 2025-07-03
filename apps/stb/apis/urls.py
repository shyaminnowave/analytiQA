from django.urls import path
from apps.stb.apis.views import LanguageListView, LanguageDetailView, StbManufactureListView, \
    StbManufactureDetailView, NatCoAPIView, NatCoOptionView, LanguageOptionView, \
    DeviceOptionView, NatCoDetailAPIView, NatcoInfoView, STBRunnerAPIView, NatCoReleaseOptionView, \
    NatCoFirmwareDetailView, NatCoFirmwareView, NatCoFirmwareOptionView, GetSTBBranchAPI, STBRunnerAPIView, \
    STBRunnerPackAPIView, STBTestcaseView, StbSchedulerView

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

    # NatCoRelease
    path('natco-releases', NatcoInfoView.as_view()),

    # NatCoFirmware
    path('firmware', NatCoFirmwareView.as_view(), name='natCo-firmware'),
    path('firmware/<int:id>', NatCoFirmwareDetailView.as_view(), name='firmware-detail'),

    # STB Branches API
    path('branches', GetSTBBranchAPI.as_view(), name='get-stb-branch'),
    path('stb-runner', STBRunnerPackAPIView.as_view(), name='get-stb-runner'),
    path('stb-testcases', STBTestcaseView.as_view(), name='get-stb-testcases'),

    # STB Runner API
    path('stb-run', STBRunnerAPIView.as_view(),  name='stb-runner'),

    # STB Scheduler API
    path('stb-scheduler', StbSchedulerView.as_view(), name='stb-scheduler'),

    # Option API endpoints
    path('natCo-option', NatCoOptionView.as_view(), name='natCo-option'),
    path('language-option', LanguageOptionView.as_view(), name='language-option'),
    path('device-option', DeviceOptionView.as_view(), name='device-option'),
    path('firmware-option', NatCoFirmwareOptionView.as_view(), name='firmware-option'),
    path('natco-release', NatCoReleaseOptionView.as_view(), name='natco-release'),

]
