import logging
from django.http import request
from django.urls import reverse
from urllib3 import proxy_from_url

logger = logging.getLogger(__name__)


class UrlBuilder:
    """
    Url Builder for Creating Urls to Specific model Instance
    """
    domain = "http://localhost:8000"

    url_patterns = {
        "testcase": {
            "list": 'testcase-list',
            "get": 'testcase-details',
        },
        "testcase_script": {
            "list": 'script-list',
            "get": 'testcase-script-detail',
        },
        "issues": {
            "list": 'issue-list',
            "get": 'issue-details',
        }
    }

    @classmethod
    def get_model_url_pattern(cls, model_name, url_type='get'):
        """Get URL pattern for a specific model"""
        model_patterns = cls.url_patterns.get(model_name.lower())
        if model_patterns:
            return model_patterns.get(url_type)
        return None

    @classmethod
    def build_url(cls, model_instance, url_type='get', request=None, **kwargs):
        print('one')
        if not model_instance:
            return None
        model_name = model_instance.lower()
        try:
            if url_type == 'get':
                url_pattern = cls.get_model_url_pattern(model_name, url_type)
                url = reverse(url_pattern, kwargs={'id': kwargs.get('object_id', None)})
            else:
                url_pattern = cls.get_model_url_pattern(model_name, url_type)
                url = reverse(url_pattern)
            return url
        except Exception as e:
            logging.error(str(e))
            return None

    @classmethod
    def build_url_with_params(cls, url_name, url_params=None, request=None):
        """Build URL with custom parameters"""
        if not url_name:
            return None

        try:
            url = reverse(url_name, kwargs=url_params or {})
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception as e:
            logging.error(str(e))
            return None

    @classmethod
    def get_url_for_notification(cls, notification, request=None):
        """Get URL for a notification's related object"""
        # First try to use stored URL name and params
        if notification.url_name:
            return cls.build_url_with_params(
                notification.url_name,
                notification.url_params,
                request
            )

        # Fallback to content object
        if notification.content_object:
            return cls.build_url(notification.content_object, request=request)

        return None

    @classmethod
    def register_model_patterns(cls, model_name, patterns):
        """Register URL patterns for a model"""
        cls.url_patterns[model_name.lower()] = patterns
