from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.urls import path, include



class MainSchemaView(SpectacularAPIView):

    patterns = [
        path('stb/', include('apps.stb.urls')),
        path('api/auth/', include('apps.account.apis.urls', namespace='account')),
        path('api/stb/', include('apps.stb.apis.urls', namespace='stb')),
        path('api/core/', include('apps.core.apis.urls')),
        path('api/general/', include('apps.general.apis.urls')),
    ]


    def get_spectacular_settings(self):
        return {
            'TITLE': 'Main API Documentation',
            'DESCRIPTION': 'Combined API documentation for App1, App2, and App3',
            'VERSION': '1.0.0',
        }
    

class SanitySchemaView(SpectacularAPIView):

    patterns = [
        path('api/nightly_sanity/', include('apps.nightly_sanity.apis.urls', namespace='nightly_sanity')),
    ]

    def get_spectacular_settings(self):
        return {
            'TITLE': 'App4 API Documentation', 
            'DESCRIPTION': 'Separate API documentation for App4',
            'VERSION': '1.0.0',
        }
    

class MainAppsSwaggerView(SpectacularSwaggerView):
    schema_url_name = 'main-schema'


class SanitySwaggerView(SpectacularSwaggerView):
    schema_url_name = 'sanity-schema'