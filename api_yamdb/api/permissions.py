from rest_framework import permissions


class OnlyAdmin(permissions.BasePermission):
    message = 'Доступ разрешен только администратору.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return(
                request.user.role.lower() == 'admin'
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
