import datetime as dt

from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User #Role


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

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        confirmation_code = default_token_generator.make_token(user)
        # отправляем письмо пользователю
        send_mail(
            subject="Код подтверждения регистрации",
            message=(
                f"Код подтверждения регистрации ниже \n "
                f"{confirmation_code}. \n Имя пользователя "
                f"{validated_data}"
            ),
            from_email=None, #"admin@yamdb.ru",
            recipient_list=[
                validated_data["email"],
            ],
        )
        return user

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
        #choices=Role.choices,
        required=False,
        # default=User.USER, #added
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
        validators=[UniqueValidator(queryset=Genre.objects.all())], # №11. валидатор должен работать корректно. Перепроверил по документации.
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



# class TitleSerializerList(serializers.ModelSerializer):
#     description = serializers.CharField(required=False)
#     genre = GenreSerializer(
#         many=True,
#         read_only=True,
#     )
#     category = CategorySerializer(read_only=True)
#     rating = serializers.SerializerMethodField()

#     def get_rating(self, obj):
#         reviews = Review.objects.filter(title__name=obj.name)
#         rating = 0
#         length = len(reviews)

#         if length > 0:
#             for i in reviews:
#                 rating += i.score
#             rating //= length
#             return rating

#         return None

#     class Meta:
#         model = Title
#         fields = (
#             "id",
#             "name",
#             "year",
#             "description",
#             "genre",
#             "category",
#             "rating",
#         )


# class TitleSerializer(serializers.ModelSerializer):
#     description = serializers.CharField(required=False)
#     genre = serializers.SlugRelatedField(
#         slug_field="slug",
#         queryset=Genre.objects.all(),
#         many=True,
#     )
#     category = serializers.SlugRelatedField(
#         slug_field="slug",
#         queryset=Category.objects.all(),
#     )

#     class Meta:
#         model = Title
#         fields = (
#             "id",
#             "name",
#             "year",
#             "description",
#             "genre",
#             "category",
#         )

#     def validate_year(self, value):
#         year = dt.date.today().year
#         if value > year:
#             raise serializers.ValidationError("Проверьте год!")
#         return value



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
            "author",
            "score",
            "text",
            "pub_date",
        )


class ReviewsSerializerPost(ReviewsSerializer):

    def validate(self, data):
        title = self.context.get("view").kwargs["title_id"]
        user = self.context["request"].user
        if user.reviews.filter(title__id=title).exists():
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
    review = ReviewsSerializer(read_only=True)

    class Meta:
        model = Comments
        fields = (
            "id",
            "author",
            "review",
            "text",
            "pub_date",
        )


# class GenreField(serializers.RelatedField):

#     def to_internal_value(self, data):
#         if len(data) == 0:
#             raise serializers.ValidationError('Поле genre должно быть заполнено')
#         genres = []
#         for i in data:
#             if i not in Genre.objects.values_list('slug', flat=True):
#                 raise serializers.ValidationError('В поле genre необходимо указать уже существующий жанр. Указанный жанр не существует.')
#             genres.append(
#                 {
#                     "name": Genre.objects.get(slug=i).name,
#                     "slug": i
#                 }
#             )
#         return genres
    
#     def to_representation(self, value):
#         return GenreSerializer(value, many=True).data


# class CategoryField(serializers.RelatedField):
#     def to_internal_value(self, data):
#         if data not in Category.objects.values_list('slug', flat=True):
#             raise serializers.ValidationError('В поле category необходимо указать уже существующую категорию. Указанной категории не существует.')
#         return {
#                 "name": Category.objects.get(slug=data).name,
#                 "slug": data
#         }
    
#     def to_representation(self, value):
#         return CategorySerializer(value).data


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
          rating=Avg('reviews__score'))[0]

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
