from rest_framework import permissions


class IsAdminOrReadOnlyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user.role == 'admin' or request.user.is_superuser
        )
