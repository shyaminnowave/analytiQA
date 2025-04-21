import re
from rest_framework import serializers
from apps.account.models import Account
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from apps.account.utils import generate_user
from django.core.exceptions import ValidationError
from rest_framework.fields import CharField
from apps.account.fields import CompanyEmailValidator
from django.contrib.auth.models import Group, Permission

User = get_user_model()


def name_validator(value):
    if value is not None and value.isalpha():
        return value
    raise ValidationError("Name Should be Alphabets Only")


class CompanyMail(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid email address.')
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validator = CompanyEmailValidator(message=self.error_messages['invalid'])
        self.validators.append(validator)


class CustomValidation(serializers.ValidationError):

    def __init__(self, message):
        super().__init__({'message': message})


class EmailExistValidation(serializers.ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Email Already Exists')
    default_code = 'Already Exists'

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)


# -------------------------- Serializer --------------------------

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True, max_length=50)
    password = serializers.CharField(required=True, max_length=50)

# -------------------------- ModelSerializer --------------------------


class AccountSerializer(serializers.ModelSerializer):

    email = CompanyMail(max_length=30)
    fullname = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=20, write_only=True)
    confirm_password = serializers.CharField(max_length=20, write_only=True)
        
    class Meta:
        model = User
        fields = ('email', 'fullname', 'password', 'confirm_password')

    def validate_email(self, value):
        if value is None:
            raise serializers.ValidationError({'email': "Email Field is should not be empty"})
        elif value:
            user_part, doamin_part = value.rsplit('@', 1)
            host, domain = doamin_part.rsplit('.', 1)
            if host == 'innowave' and domain == 'tech':
                return value
            raise serializers.ValidationError({"email": "Please Enter you Innowave Mail"})

    def validate_fullname(self, value):
        if value is None:
            raise serializers.ValidationError("Fullname Field is should not be empty")
        if re.search(r'\d', value):
            raise serializers.ValidationError("Fullname Field is should contains any Numbers")
        return value

    def validate_password(self, value):
        if value is None:
            raise serializers.ValidationError("Password Field is should not be empty")
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).+$', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter, one number, "
                                              "and one special character."
            )
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError({"password": "Password and confirm password Not Matching"})
        if User.objects.filter(email=attrs.get('email')).first():
            raise serializers.ValidationError({"email": "Email Already Exists Please Go with another Email"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = Account.objects.create_user(
            email=validated_data['email'],
            username=generate_user(),
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )
        return user


class GroupListSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):

        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        if request and request.path == '/api/auth/create-group':
            self.Meta.fields = '__all__'
        elif request and request.path == '/api/auth/group':
            self.Meta.fields = ['id', 'name']
        super(GroupListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Group
        fields = []

    def to_representation(self, instance):
        represent = super(GroupListSerializer, self).to_representation(instance)
        represent['permissions'] = [i.name for i in instance.permissions.all()]
        return represent


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'

    def to_representation(self, instance):
        response = super(GroupSerializer, self).to_representation(instance)
        response['permissions'] = [{"id": i.id, "name": i.name} for i in instance.permissions.all()]
        return response


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ('id', "name", "codename")
        ordering = ['-id']


class UserGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['name']


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['fullname', 'email', 'groups']

    def to_representation(self, instance):
        _data = super(ProfileSerializer, self).to_representation(instance)
        _data['groups'] = instance.groups.name if instance.groups else None
        _data['permissions'] = [i.name for i in instance.groups.permissions.all()] if instance.groups else None

        return _data


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['fullname', 'email', 'username', 'groups']

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['groups'] = instance.groups.name
        return represent


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('fullname', 'email', 'username', 'groups')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['groups'] = instance.groups.name
        return represent
