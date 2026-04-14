"""Сериализаторы для моделей приложения review."""

import uuid

from django.http import Http404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import EMAIL_LENGTH, MAX_NAMES_LENGTH
from users.validators import valid_username


User = get_user_model()


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

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data


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

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class MeUserSerializer(YamdbUserSerializer):
    """Сериализатор для работы с пользователями."""

    class Meta(YamdbUserSerializer.Meta):
        read_only_fields = ('role',)


class CreateUserSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=EMAIL_LENGTH, required=True)
    username = serializers.CharField(
        max_length=MAX_NAMES_LENGTH,
        required=True,
        validators=[valid_username]
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()
        if user_by_email and not user_by_username:
            raise serializers.ValidationError(
                'Пользователь с такой почтой уже существует.'
            )
        elif user_by_username and not user_by_email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.'
            )
        elif user_by_email and user_by_username:
            if user_by_email != user_by_username:
                raise serializers.ValidationError(
                    'Почта и username принадлежат разным пользователям.'
                )
        return data

    def generate_confirmation_code(self):
        """Генерирует UUID и обрезает до нужной длины."""
        return str(uuid.uuid4()).replace('-', '')[:12]

    def create(self, validated_data):
        """
        Создает пользователя, если его нет в базе данных.
        Отправляет письмо с кодом подтверждения.
        """
        username = validated_data['username']
        email = validated_data['email']

        try:
            code = self.generate_confirmation_code()
            user, created = User.objects.get_or_create(
                username=username, email=email
            )
            user.confirmation_code = code
            user.save()
            send_mail(
                subject='Подтверждение регистрации на YaMDB',
                message=(
                    'Для завершения регистрации на сайте используйте '
                    'код подтверждения: '
                    f'{code}'
                ),
                from_email='from@yamdb.com',
                recipient_list=[email],
            )
            return user
        except Exception:
            raise serializers.ValidationError(
                {'Не удалось отправить письмо с кодом подтверждения.'}
            )


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
