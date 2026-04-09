from django.db.models import Avg

from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title


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


# class TitleReadSerializer(serializers.ModelSerializer):
#     """Сериализатор для GET-запросов модели Title."""

#     genre = GenreSerializer(many=True)
#     category = CategorySerializer()
#     rating = serializers.SerializerMethodField()

#     class Meta:
#         model = Title
#         fields = '__all__'

#     def get_rating(self, obj):
#         """Возвращает средний рейтинг произведения на основе оценок отзывов."""
#         result = obj.reviews.aggregate(Avg('score'))
#         return result['score__avg']


# class TitleWriteSerializer(serializers.ModelSerializer):
#     """Сериализатор для POST-запросов модели Title."""

#     genre = serializers.SlugRelatedField(
#         slug_field='slug',
#         queryset=Genre.objects.all(),
#         many=True,
#     )
#     category = serializers.SlugRelatedField(
#         slug_field='slug',
#         queryset=Category.objects.all(),
#     )

#     class Meta:
#         model = Title
#         fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title"""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        """Возвращает средний рейтинг произведения на основе оценок отзывов."""
        result = obj.reviews.aggregate(Avg('score'))
        return result['score__avg']

    def to_representation(self, instance):
        """При чтении возвращает genre и category как вложенные объекты."""
        data = super().to_representation(instance)
        data['genre'] = GenreSerializer(instance.genre.all(), many=True).data
        data['category'] = CategorySerializer(instance.category).data
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('pub_date', 'title')

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
        fields = '__all__'
        read_only_fields = ('pub_date', 'review')
