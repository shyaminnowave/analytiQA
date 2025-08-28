from django.urls import path
from apps.nightly_sanity.apis.views import ReleaseListView, ApkListView, NatcoListView, NatcoBuildView, BuildMetrixView, TestFunctionalityListView, \
                                            CompareBuildsAPI, BuildFailureViewAPI, NatcoTotalRunsAPI


app_name = 'nightly_sanity'

urlpatterns = [
    path('releases/', ReleaseListView.as_view(), name='release-list'),
    path('apk-files/', ApkListView.as_view(), name='apk-list'),
    path('natco/', NatcoListView.as_view(), name='natco-list'),
    path('functionality/', TestFunctionalityListView.as_view(), name='test-functionality-list'),
    path('natco-overview/', BuildMetrixView.as_view(), name='natcos-overview'),  
    path('natco-filter/', CompareBuildsAPI.as_view(), name='compare-builds'),
    path('failure-details/', BuildFailureViewAPI.as_view(), name='failure-details'),
    path('iterations/', NatcoTotalRunsAPI.as_view(), name="testing"),
    path('natco-build/<str:natco>', NatcoBuildView.as_view(), name='natco-build'), 
]