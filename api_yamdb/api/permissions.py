from rest_framework import permissions


class OnlyAdmin(permissions.BasePermission):
    message = "Доступ разрешен только администратору."

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                request.user.is_admin
                or request.user.is_staff
                or request.user.is_superuser
            )
        return False


class OnlyOwnAccount(permissions.BasePermission):
    message = "Доступ разрешен только к своему аккаунту."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and request.user == obj)


class OwnerOrReadOnlyList(permissions.BasePermission):
    message = "Изменение данных доступно только владельцу."

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class AdminOrModerator(permissions.BasePermission):
    message = "Доступ разрешен только администраторам и модераторам."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_admin
            or request.user.is_moderator
        )


class ReadOnly(permissions.BasePermission):
    message = "Разрешено только чтение."

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
