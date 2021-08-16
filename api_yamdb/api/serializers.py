from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from users.models import ROLE_CHOICES, User


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
