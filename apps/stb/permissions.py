from rest_framework.permissions import DjangoModelPermissions, BasePermission


class LangaugeOptionPermission(DjangoModelPermissions):

    perms_map = {
        'GET': ['stb.view_language_option']
    }


class NatCoOptionPermission(DjangoModelPermissions):

    perms_map = {
        'GET': ['stb.view_natco_option']
    }


class DeviceOptionPermission(DjangoModelPermissions):

    perms_map = {
        'GET': ['stb.view_stb_option']
    }


class AdminPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Admin'))


class LanguagePermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('stb.view_language'))

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'PUT', 'DELETE']:
            if request.method == 'GET':
                return bool(request.user and request.user.has_perm('stb.view_langugae'))
            if request.method == 'PUT':
                return bool(request.user and request.user.has_perm('stb.change_language'))
            if request.method == 'DELETE':
                return bool(request.user and request.user.has_perm('stb.delete_language'))
        return False


class DevicePermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('stb.view_stbs_manufacture'))

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'PUT', 'DELETE']:
            if request.method == 'GET':
                return bool(request.user and request.user.has_perm('stb.view_stbs_manufacture'))
            if request.method == 'PUT':
                return bool(request.user and request.user.has_perm('stb.change_stbs_manufacture'))
            if request.method == 'DELETE':
                return bool(request.user and request.user.has_perm('stb.delete_stbs_manufacture'))
        return False


class NatcoPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('stb.view_natco'))

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'PUT', 'DELETE']:
            if request.method == 'GET':
                return bool(request.user and request.user.has_perm('stb.view_natco'))
            if request.method == 'PUT':
                return bool(request.user and request.user.has_perm('stb.change_natco'))
            if request.method == 'DELETE':
                return bool(request.user and request.user.has_perm('stb.delete_natco'))
        return False
