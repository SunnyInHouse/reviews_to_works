from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# ROLE_CHOICES = (
#     ("user", "пользователь"),
#     ("moderator", "модератор"),
#     ("admin", "администратор"),
# )
class Role(models.TextChoices):
    ADMIN = "admin", _("администратор")
    MODERATOR = "moderator", _("модератор")
    USER = "user", _("пользователь")



class User(AbstractUser):
    # password = None
    # is_staff = None
    # is_active = None
    # is_superuser = None
    # date_joined = None

    email = models.EmailField(
        "Адрес e-mail",
        unique=True,
        error_messages={
            "unique": "Пользователь с указанным e-mail уже зарегистрирован.",
        },
    )
    bio = models.TextField(
        "Биография",
        blank=True,
    )
    role = models.CharField(
        "Роль пользователя",
        #choices=ROLE_CHOICES,
        choices = Role.choices,
        max_length=15,
        #default="user",
        default = Role.USER,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

# это ограничение не актуально, тк и так оба парметры уникальны
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["email", "username"],
        #         name="unique_username_email"
        #     )
        # ]

# этот метод не нужен, тк уже определен в abstractUser
    # def __str__(self):
    #     return f"{self.username}"
 # ADDED METHODS
    @property
    def is_admin(self, request):
        return request.user.role == Role.ADMIN
    
    @property
    def is_moderator(self, request):
        return request.user.role == Role.MODERATOR
    
    @property
    def is_user(self, request):
        return request.user.role == Role.USER
