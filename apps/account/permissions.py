from rest_framework.permissions import BasePermission


class AdminUserPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Admin').exists())

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.groups.filter(name='Admin').exists())


class TechnicalTesterUserPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='TechnicalTester').exists())

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.groups.filter(name='TechnicalTester').exists())


class AccountPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.has_perm('auth.view_group'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ['POST', 'PUT', 'DELETE']:
            return (
                    request.user.has_perm('account.change_account') or
                    request.user.has_perm('account.delete_account')
            )
        return False


class GroupCreatePermission(BasePermission):

    def has_permission(self, request, view):
        return bool if request.user.has_perm('auth.create_group') else False

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'DELETE']:
            return (
                request.user.has_perm('auth.change_group') or
                request.user.has_perm('auth.delete_group')
            )
        return False