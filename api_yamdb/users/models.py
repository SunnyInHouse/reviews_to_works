from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('user', 'пользователь'),
    ('moderator', 'модератор'),
    ('admin', 'администратор'),
)


class User(AbstractUser):

    email = models.EmailField(
        "Адрес e-mail",
        unique=True,
        error_messages={
            'unique': "Пользователь с указанным e-mail уже зарегистрирован.",
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
        default="user",
    )

    def __str__(self):
        return f'{self.username} status {self.is_active}'

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username", )

        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_username_email'
            )
        ]