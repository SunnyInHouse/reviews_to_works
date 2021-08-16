from django.db import models
from users.models import User


# временно создаю этот класс, чтобы можно было тестировать
class Titles(models.Model):
    name = models.TextField(verbose_name="Содержание отзыва")
    year = models.IntegerField(verbose_name="Год")
    category_id = models.IntegerField(verbose_name="Категория")


class Reviews(models.Model):
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        verbose_name="Отзывы",
        related_name="reviews",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор отзыва",
        related_name="reviews",
    )
    score = models.IntegerField(verbose_name="Оценка")
    text = models.TextField(verbose_name="Содержание отзыва")
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата отзыва"
    )


class Comments(models.Model):
    review = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        verbose_name="Комментарии к отзыву",
        related_name="comment",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор комментария",
        related_name="comment",
    )
    text = models.TextField(verbose_name="Содержание отзыва")
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата комментария"
    )
