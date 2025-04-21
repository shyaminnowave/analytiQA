from rest_framework.permissions import DjangoModelPermissions, BasePermission


class TestCaseViewPermission(DjangoModelPermissions):

    perms_map = {
        'GET': ['core.view_testcase']
    }


class TestCasePermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('core.view_testcase'))