from rest_framework import permissions


class OnlyAdmin(permissions.BasePermission):
    message = 'Доступ разрешен только администратору.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return(
                request.user.role == 'admin'
                or request.user.is_staff
                or request.user.is_superuser
            )
        return False


class OnlyOwnAccount(permissions.BasePermission):
    message = 'Доступ разрешен только к своему аккаунту.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return(
                request.user.role == 'admin'
                or request.user.role == 'user'
                or request.user.role == 'moderator'
            )
        return False


class OwnerOrReadOnlyList(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return (
                obj.author == request.user or
                request.user.role == 'admin' or
                request.user.role == 'moderator'
        )


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        return False
