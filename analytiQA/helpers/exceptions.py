from rest_framework.exceptions import APIException, ValidationError, ReturnDict, ReturnList, force_str, ErrorDetail
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from rest_framework.views import exception_handler


def _get_error_details(data, default_code=None):
    """
    Descend into a nested data structure, forcing any
    lazy translation strings or strings into `ErrorDetail`.
    """
    if isinstance(data, (list, tuple)):
        ret = [
            _get_error_details(item, default_code) for item in data
        ]
        if isinstance(data, ReturnList):
            return ReturnList(ret, serializer=data.serializer)
        return ret
    elif isinstance(data, dict):
        ret = {
            key: _get_error_details(value, default_code)
            for key, value in data.items()
        }
        if isinstance(data, ReturnDict):
            return ReturnDict(ret, serializer=data.serializer)
        return ret

    text = force_str(data)
    code = getattr(data, 'code', default_code)
    return ErrorDetail(text, code)


class CustomFieldException(APIException):

    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = 'Invalid Data'
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]
        self.detail = _get_error_details(detail, code)

    
class TokenExpireException(APIException):

    status = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Stb Token Expired')
    default_code = 'authentication_failed'


class QAException(Exception):

    default_detail = 'Invalid Data'
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code

    def __str__(self):
        return self.detail if self.detail is not None else self.default_detail

    def __repr__(self):
        return self.detail if self.detail is not None else self.default_detail


class NotModelException(Exception):
    """
    Exception
    """
    pass


def custom_exception_handler(exc, context):
    """
    Custom exception handler to return validation errors in the desired format.
    """
    # Get the standard DRF response
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        # Reformat validation error messages
        formatted_errors = {}
        for field, errors in response.data.items():
            if isinstance(errors, list):
                # Use the first error message in the list
                formatted_errors[field] = errors[0]
            else:
                formatted_errors[field] = errors

        # Replace the response structure
        response.data = {
            "status": False,
            "status_code": response.status_code,
            "data": None,
            "message": formatted_errors,
        }
    return response
