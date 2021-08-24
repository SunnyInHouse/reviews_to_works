import datetime as dt

from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import Avg, IntegerField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User


class AuthSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        model = User
        fields = ("username", "email")
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=("username", "email"),
                message=(
                    "Задано не уникальное сочетание полей email " "и username."
                ),
            )
        ]


    def validate_username(self, value):
        # проверяем что в поле user передано не me
        if value == "me":
            raise serializers.ValidationError(
                "Нельзя использовать для username имя me."
            )
        return value


class TokenDataSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = get_object_or_404(User, username=data["username"])
        if not default_token_generator.check_token(
            user, data["confirmation_code"]
        ):
            raise serializers.ValidationError(
                "Неверный код подтверждения для указанного username"
            )
        return data


class UsersSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=False,
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_field = (
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=("username", "email"),
                message=(
                    "Задано не уникальное сочетание полей email " "и username."
                ),
            )
        ]

    def validate_username(self, value):
        # проверяем что в поле user передано не me
        if value == "me":
            raise serializers.ValidationError(
                "Нельзя использовать для username имя me."
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Genre.objects.all())],
    )

    class Meta:
        model = Genre
        fields = ("name", "slug")


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Category.objects.all())],
    )

    class Meta:
        model = Category
        fields = ("name", "slug")


class ReviewsSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "text",
            "author",
            "score",
            "pub_date",
        )

    def validate(self, data):
        title = self.context.get("view").kwargs["title_id"]
        user = self.context["request"].user
        if (
                user.reviews.filter(title__id=title).exists()
                and self.context["request"].method != "PATCH"
        ):
            raise ValidationError(
                "Нельзя публиковать более 1 отзыва на произведение"
            )
        return data

    def validate_score(self, value):
        if 10 >= value >= 1:
            return value
        raise serializers.ValidationError(
            "Оценка должна находиться в диапазоне [1..10]"
        )


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comments
        fields = (
            "id",
            "text",
            "author",
            "pub_date",
        )


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    description = serializers.CharField(required=False)
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
            "rating",
        )

    def get_rating(self, obj):
        title = Title.objects.filter(name=obj.name).annotate(
            rating=Avg('reviews__score', output_field=IntegerField()))[0]
        return title.rating

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError("Проверьте год!")
        return value

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['genre'] = GenreSerializer(instance.genre, many=True).data
        response['category'] = CategorySerializer(instance.category).data
        return response
