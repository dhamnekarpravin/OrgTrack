from rest_framework.permissions import BasePermission

from .services import permission_codes


def _portal(request):
    token = request.auth
    return token.get("portal") if token is not None else None


class PasswordChanged(BasePermission):
    """Blocks a user who still has the temporary password."""

    message = "You must change your password first."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return True
        if getattr(view, "allow_password_change_pending", False):
            return True
        return not user.must_change_password


class IsPlatformPortal(BasePermission):
    message = "This page is only for the Platform website."

    def has_permission(self, request, view):
        return _portal(request) == "platform" and request.user.school_id is None


class IsSchoolPortal(BasePermission):
    message = "This page is only for the School/College website."

    def has_permission(self, request, view):
        return _portal(request) == "school" and request.user.school_id is not None


def require(code):
    """Use like: permission_classes = [require("student_marks.create")]"""

    class _Require(BasePermission):
        message = "You do not have permission for this action."

        def has_permission(self, request, view):
            return code in permission_codes(request.user)

    return _Require