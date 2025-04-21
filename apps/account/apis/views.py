import logging
from typing import Any
from rest_framework.views import Response
from rest_framework import generics
from apps.account.models import Account
from apps.account.apis.serializers import AccountSerializer, LoginSerializer, ProfileSerializer, UserListSerializer, \
    PermissionSerializer, GroupListSerializer, GroupSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework import status
from apps.account.utils import get_token_for_user
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.account.signals import user_token_login, user_token_logout
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, \
    extend_schema_view
from apps.core.apis.views import CustomPagination
from django.contrib.auth.models import Group, Permission
from analytiQA.helpers.renders import ResponseInfo
from analytiQA.helpers import custom_generics as cgenerics
from analytiQA.helpers.exceptions import TokenExpireException
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http.response import Http404
from apps.account.token import user_token_generator

User = get_user_model()
logging = logging.getLogger(__name__)


# ------------------------------ ListAPIS ------------------------------


@extend_schema(
    summary="Retrieve a list of all permissions",
    description="""
    This endpoint allows authenticated users to retrieve a list of all available permissions in the system. 
    Each permission represents a specific type of access control or action that can be assigned to users or roles. 
    The response will contain a paginated list of permissions, where each permission includes its unique ID and associated details. 

    **Access Control:** Only accessible by admin users or users with specific permission to view the list of permissions.""",
    tags=['Account Module APIS']
)
class PermissionListView(generics.ListAPIView):
    # permission_classes = [AdminUserPermission]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


@extend_schema(
    summary="Retrieve a list of user groups",
    description="""
    This endpoint allows authorized users to retrieve a list of all user groups within the system. 
    Each group is a collection of users that share a common set of permissions. The groups are used 
    for access control and role-based permission assignment.

    The API will return a paginated list of groups, each containing details such as the group's name and other relevant attributes.

    **Access Control:** 
    - Only users with the appropriate permissions can access this endpoint.
    """,
    tags=['Account Module APIS']
)
class GroupView(generics.ListAPIView):
    # permission_classes = [UserPermission]
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer

    def get_serializer_context(self):
        return {"request": self.request}


@extend_schema(
    summary="Retrieve a list of users with minimal details",
    description="""
    This endpoint allows authorized users to retrieve a paginated list of all user accounts in the system. 
    The response includes basic user information such as the full name, username, email, and the groups to which the users belong.
    
    **Access Control:** 
    - Only users with the proper permissions (e.g., admin or staff) can access this endpoint.
    The response is paginated, with pagination controlled by the custom `CustomPagination` class.
    """,
    responses={200: UserListSerializer(many=True)},
    tags=['Account Module APIS']
)
class UserListView(generics.ListAPIView):
    # permission_classes = [UserPermission]
    serializer_class = UserListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = User.objects.only(
            'fullname',
            'username',
            'email',
            'groups').prefetch_related('groups').all()
        return queryset


# ------------------------------ APIViews ------------------------------
@extend_schema(
    summary="Logout a user by blacklisting the JWT token",
    description="""
    This endpoint allows authenticated users to log out by blacklisting their JWT refresh token. 
    Upon receiving a valid refresh token, it ensures that the user is logged out and their token is invalidated, 
    preventing further access with that token.

    **Access Control:**
    - Users must be authenticated via JWT authentication to access this endpoint.
    """,
    tags=['Account Module APIS']
)
class LogoutView(APIView):

    def __init__(self, **kwargs: Any) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            if request.user.is_authenticated and isinstance(request.user, Account):
                user_token_logout.send(sender=request.user.__class__, user=request.user, request=request)
                token.blacklist()
                self.response_format['status'] = True
                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format['message'] = "User Logout Successfull"
                return Response(self.response_format, status=status.HTTP_200_OK)
        except Exception as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)


# ------------------------------ Generic APIS ------------------------------

@extend_schema(
    summary="User login",
    description="""
    This endpoint allows users to log in by providing their email and password. 
    On successful authentication, it returns an access and refresh token, along with the user's email and username.
    **Access Control:** 
    - No authentication is required to access this endpoint.
    """,
    tags=['Account Module APIS']
)
class LoginView(generics.GenericAPIView):

    def __init__(self, **kwargs: Any) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                default_errors = {field: error[0] for field, error in serializer.errors.items()}
                self.response_format['status'] = False
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format['message'] = default_errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            user_cred = self._perform_login(request, email=serializer.validated_data.get('email', None),
                                            password=serializer.validated_data.get('password', None))

            if user_cred is not None:
                self.response_format['status'] = True
                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format['data'] = user_cred
                self.response_format['message'] = "User Login Successfull"
                response = Response(self.response_format,
                                    status=status.HTTP_200_OK)
                return response
            else:
                self.response_format['status'] = False
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format['data'] = user_cred
                self.response_format['message'] = {
                    "error": "Email or Password Not Match, Please enter the Correct Details"
                }
                return Response(self.response_format,
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
            self.response_format['message'] = str(e)
            return Response({'success': False, 'error': "Please Check the login credentials"},
                            status=status.HTTP_404_NOT_FOUND)

    def _perform_login(self, request, email, password):
        user = authenticate(email=email, password=password)
        print('sus', user)
        if user is not None:
            user_token_login.send(sender=user, user=user, request=request)
            token = get_token_for_user(user)
            return {
                'access': token['access'],
                'refresh': token['refresh'],
                'email': user.email,
                'username': user.username,
            }
        return None


@extend_schema(
    summary="Retrieve user profile by username",
    description="""
    This endpoint retrieves the profile information of a user by their username.

    The API allows users to fetch their profile details, including the full name, email, 
    and groups associated with the account. The user is identified by their unique username.
    **Access Control:** Specific permissions may be required to access this endpoint.
    """,
    tags=['Account Module APIS']
)
class UserProfileView(cgenerics.CustomRetriveAPIVIew):
    serializer_class = ProfileSerializer
    lookup_field = 'username'

    def get_object(self):
        queryset = User.objects.only(
            "fullname",
            "email",
            "groups"
        ).select_related(
            "groups"
        ).get(
            username=self.kwargs.get("username")
        )
        return queryset


# ------------------------------ CustomGeneric APIS ------------------------------

@extend_schema(
    summary="Create a new user account",
    description=(
            "Account Create API which takes Email, Fullname, and Password.\n\n"
            "**Important:** The email must be from the domain `@innowave.tech`.\n\n"
            "**Important:** Ensure the password is at least 8 characters long, "
            "contains both uppercase and lowercase letters, and includes at least one special character."
    ),
    tags=['Account Module APIS']
)
class AccountCreateView(cgenerics.CustomCreateAPIView):
    serializer_class = AccountSerializer


@extend_schema(
    summary="Update user group by username",
    description=(
            "This endpoint allows an admin to update the group(s) associated with a user identified by their username.\n\n"
    ),
    tags=['Account Module APIS']
)
class UserUpdateGroup(cgenerics.CustomRetrieveUpdateAPIView):
    # permission_classes = [AdminUserPermission]
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_object(self):
        queryset = User.objects.get(emai=self.lookup_field)
        return queryset


@extend_schema(
    summary="Create a new group",
    description=(
            "This endpoint allows an admin to create a new group.\n\n"
    ),
    tags=['Account Module APIS']
)
class GroupCreateView(cgenerics.CustomCreateAPIView):
    # permission_classes = [DjangoModelPermissions]

    queryset = Group.objects.all()
    serializer_class = GroupListSerializer

    def post(self, request, *args, **kwargs):
        response = super(GroupCreateView, self).post(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})


@extend_schema(
    summary="Retrieve or update a specific group",
    description=(
            "This endpoint allows an admin to retrieve or update a group identified by its primary key (ID).\n\n"
    ),
    tags=['Account Module APIS']
)
class GroupDetailView(cgenerics.CustomRetrieveUpdateAPIView):
    # permission_classes = [DjangoObjectPermissions]
    serializer_class = GroupSerializer
    lookup_field = 'pk'

    def get_object(self):
        queryset = Group.objects.get(
            id=self.lookup_field
        )
        return queryset


@extend_schema(
    summary="Retrieve users associated with a specific group",
    description=(
            "This endpoint allows you to retrieve a list of users associated with a specific group.\n\n"
    ),
    tags=['Account Module APIS']
)
class GroupUsers(cgenerics.CustomRetriveAPIVIew):

    def get_queryset(self):
        queryset = Group.objects.select_related('groups').all()
        return queryset

    serializer_class = ProfileSerializer


class UserActivateView(APIView):

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        try:
            user_instance = get_object_or_404(User, email=request.data.get('email'))
            if user_instance:
                check_token = user_token_generator(user_instance, token)
                if check_token:
                    user_instance.is_active = True
                    user_instance.save()
                    return Response("User Activated")
                return Response("Token Error")
            else:
                return Response("no instance")
        except Http404 as e:
            logging.error(str(e))
            return Response("func error")
        except Exception as e:
            logging.error(str(e))


@extend_schema(
    summary="Retrieve Access Token",
    description=(
            "The endpoint allows you to retrieve a Access Token"
    )
)
class AccountTokenAccessView(TokenViewBase):
    serializer_class = TokenRefreshSerializer

    def __init__(self, **kwargs: Any) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            self.response_format['status'] = True
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format['data'] = response.data
            self.response_format['message'] = "Success"
            return Response(self.response_format, status=status.HTTP_200_OK)
        except TokenExpireException as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
            self.response_format['data'] = None
            self.response_format['message'] = e.default_detail
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
