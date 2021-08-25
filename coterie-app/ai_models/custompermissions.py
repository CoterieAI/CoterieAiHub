from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUserOrReadonly(BasePermission):
    message = "only admins can create or modify models"

    def has_permission(self, request, view):
        is_admin = request.user.is_superuser
        if request.method in SAFE_METHODS:
            return True
        return is_admin
