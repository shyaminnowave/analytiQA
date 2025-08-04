from django.urls import path
from apps.nightly_sanity.apis.views import ReleaseListView, ApkListView, NatcoListView, NatcoBuildView, BuildMetrixView, TestFunctionalityListView


app_name = 'nightly_sanity'

urlpatterns = [
    path('releases/', ReleaseListView.as_view(), name='release-list'),
    path('apk-files/', ApkListView.as_view(), name='apk-list'),
    path('natco/', NatcoListView.as_view(), name='natco-list'),
    path('functionality/', TestFunctionalityListView.as_view(), name='test-functionality-list'),
    path('get-graph-data/', BuildMetrixView.as_view(), name='get-graph-data'),  # Assuming this is a view for graph data
    path('natco-build/<str:natco>', NatcoBuildView.as_view(), name='natco-build'),  # Assuming this is a view for listing builds by NATCO
]