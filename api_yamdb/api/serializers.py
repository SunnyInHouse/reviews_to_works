import datetime as dt

from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from users.models import ROLE_CHOICES, User
from reviews.models import Review, Comments, Title, Genre, Category


class AuthSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email'),
                message=('Задано не уникальное сочетание полей email '
                         'и username.')
            )
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, is_active=False)
        confirmation_code = default_token_generator.make_token(user)
        # отправляем письмо пользователю
        send_mail(
            subject='Код подтверждения регистрации',
            message=(f'Код подтверждения регистрации ниже \n '
                     f'{confirmation_code}. \n Имя пользователя '
                     f'{validated_data}'),
            from_email='admin@yamdb.ru',
            recipient_list=[validated_data['email'], ],
        )
        return user

    def validate_username(self, value):
        # проверяем что в поле user передано не me
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать для username имя me.'
            )
        return value


class TokenDataSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(
            user, data['confirmation_code']
        ):
            raise serializers.ValidationError(
                'Неверный код подтверждения для указанного username'
            )
        user.is_active = True
        user.save()
        return data


class UsersSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        read_only_field = ('first_name', 'last_name', 'bio', 'role', )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email'),
                message=('Задано не уникальное сочетание полей email '
                         'и username.')
            )
        ]

    def validate_username(self, value):
        # проверяем что в поле user передано не me
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать для username имя me.'
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleSerializerList(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class TitleSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год!')
        return value

    def get_rating(self, obj):
        scores = obj.reviews.all()

        # print("self.data = ", self.data)
        # print("self['context']['data'].reviews.all() = ", self['context']['data'].reviews.all())
        print('self = ', self)
        print('obj = ', obj.reviews.all())
        print('scores = ', scores)

        rating = None
        length = len(scores)

        if length > 0:
            rating = 0
            for i in scores:
                rating += i['score']
            rating //= length
        return rating


class ReviewsSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        fields = ('id', 'author', 'score', 'text', 'pub_date')
        model = Review

    # def validate(self, data):
    #     if self.context["request"].user.reviews.exists():
    #         raise ValidationError('Нельзя публиковать более 1 отзыва на произведение')
    #     return data

    def validate_score(self, value):
        if 10 >= value >= 1:
            return value
        raise serializers.ValidationError(
            "Оценка должна находиться в диапазоне [1..10]"
        )


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)
    review = ReviewsSerializer(read_only=True)

    class Meta:
        fields = "__all__"
        model = Comments
