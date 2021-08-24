from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    ROLE_CHOICES = (
        (USER, "пользователь"),
        (MODERATOR, "модератор"),
        (ADMIN, "администратор"),
    )

    # class Role(models.TextChoices):
    #     ADMIN = "admin", _("администратор")
    #     MODERATOR = "moderator", _("модератор")
    #     USER = "user", _("пользователь")


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
        choices=ROLE_CHOICES,
        # choices = Role.choices,
        max_length=15,
        default=USER,
        # default = Role.USER,
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
    def is_admin(self):
        return self.role == User.ADMIN
    
    @property
    def is_moderator(self):
        return self.role == User.MODERATOR
    
    @property
    def is_user(self):
        return self.role == User.USER
