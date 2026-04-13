"""Сериализаторы для моделей приложения review."""
import re

from django.http import Http404
from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


def validate_username_and_email(username, email):
    user_by_email = User.objects.filter(email=email).first()
    user_by_username = User.objects.filter(username=username).first()
    if user_by_email and not user_by_username:
        return False
    elif user_by_username and not user_by_email:
        return False
    elif user_by_email and user_by_username:
        if user_by_email != user_by_username:
            return False
    return True


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для GET-запросов модели Title."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для POST/PATCH-запросов модели Title."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_null=False,
        allow_empty=False,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Запрещает повторный отзыв от одного автора на одно произведение."""
        if self.instance is not None:
            return data
        request = self.context.get('request')
        title = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=request.user, title_id=title).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class YamdbUserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователями."""

    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)
    role = serializers.ChoiceField(
        choices=['user', 'moderator', 'admin'],
        required=False,
        default='user'
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if not validate_username_and_email(username, email):
            raise serializers.ValidationError(
                'Имя пользователя или пароль уже используются.'
            )
        return data

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Username должен содержать только буквы, '
                'цифры и символы @/./+/-/_.'
            )
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
            'confirmation_code'
        )
        extra_kwargs = {
            'confirmation_code': {'required': False, 'write_only': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'bio': {'required': False, 'allow_blank': True}
        }


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для работы с токенами."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if not username or not confirmation_code:
            raise serializers.ValidationError(
                'Поля username и confirmation_code обязательны'
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404('Пользователь не найден')

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )
        data['user'] = user
        return data
