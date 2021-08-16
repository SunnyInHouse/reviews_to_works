import datetime as dt

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Title, Genre, Category


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
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleSerializerList(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

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

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        year = dt.date.today().year
        if not value > year:
            raise serializers.ValidationError('Проверьте год!')
        return value
