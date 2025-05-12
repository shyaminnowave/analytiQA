from rest_framework.permissions import DjangoModelPermissions, BasePermission, SAFE_METHODS


class TestCaseViewPermission(DjangoModelPermissions):

    perms_map = {
        'GET': ['core.view_testcase']
    }


class TestCasePermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('core.view_testcase'))


class CommentPermission(BasePermission):

    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        # Allow safe methods for all users
        if request.method in SAFE_METHODS:
            return True

        # Only allow update or delete if the user is the owner of the comment
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.user == request.user

        return False
            
    

class TestCaseUpdatePermission(BasePermission):
    
    def has_permission(self, request, view):
        return True

    field = "automation_status"
    def has_object_permission(self, request, view, obj):
        if request.method in ["PUT", "PATCH"]:
            status = request.data.get('automation_status', '').lower()
            if status == 'ready':
                if request.user.groups:
                    return request.user.has_perm("core.can_change_status_to_review")
                return False
            if status == 'review':
                if request.user.groups:
                    return request.user.has_perm("core.can_change_status_to_ready")
                return False
        return True