from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    ROLE_CHOICES = (
        (USER, "пользователь"),
        (MODERATOR, "модератор"),
        (ADMIN, "администратор"),
    )

    first_name = models.CharField(
        "first name",
        max_length=150,
        blank=True
    )
    email = models.EmailField(
        "Адрес e-mail",
        unique=True,
        max_length=254,
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
        max_length=15,
        default=USER,
    )

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @property
    def is_user(self):
        return self.role == User.USER

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)
