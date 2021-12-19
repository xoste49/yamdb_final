from .models import (
    Comment,
    Review,
    Category,
    Title,
    Genre
)

from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'username',
            'email',
            'bio',
            'role',
            'first_name',
            'last_name'
        ]
        model = User


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation = serializers.CharField(max_length=50)


class ConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                    title_id=self.context['view'].kwargs['title_id'],
                    author=self.context['request'].user).exists():
                raise serializers.ValidationError(
                    'Вы уже публиковали отзыв на это произведение.'
                )
        return data

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class WriteTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReadTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(default=None)

    class Meta:
        fields = '__all__'
        model = Title
