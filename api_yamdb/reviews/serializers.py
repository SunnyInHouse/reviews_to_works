from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Reviews, Comments


class ReviewsSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        fields = "__all__"
        model = Reviews

    def validate_score(self, value):
        if 10 >= value >= 1:
            print('1validate_score value = ', value)
            return value
        print('2validate_score value = ', value)
        raise serializers.ValidationError(
            "Оценка должна находиться в диапазоне [1..10]"
        )


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        fields = "__all__"
        model = Comments
