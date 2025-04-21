from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):

    def __init__(self, *args, **kwargs):
        self.response_format = {
            "status": False,
            "status_code": None,
            "message": None,
            "data": None
        }
        super().__init__(*args, **kwargs)

    def authenticate(self, request):
        try:
            # Call the parent class's authenticate method
            return super().authenticate(request)
        except AuthenticationFailed as e:
            raise AuthenticationFailed(detail="Authorization header must contain two space-delimited values")
        except TokenError as e:
            raise AuthenticationFailed(detail="Invalid token. Please provide a valid token.")
        except Exception as e:
            raise AuthenticationFailed(detail="An unexpected error occurred during authentication.")


class ActiveUserAuthentication(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(email=username, is_active=True)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
