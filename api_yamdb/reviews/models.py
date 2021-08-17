from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.TextField()
    year = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, through='GenreTitle', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='genre_title')
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='title_genre')

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
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
        Review,
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
