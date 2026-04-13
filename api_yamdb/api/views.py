"""Представления для API приложения reviews"""

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework import (
    filters, generics, mixins, pagination, status, viewsets
)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from api.filters import TitleFilter
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    CreateUserSerializer,
    GenreSerializer,
    MeUserSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    TokenObtainSerializer,
    YamdbUserSerializer
)
from api.permissions import (
    IsAdminOrReadOnly, IsAuthorModeratorAdminOrReadOnly, IsAdmin
)


User = get_user_model()


class CategoryGenreBaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый вьюсет для категорий и жанров."""

    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_title(self):
        """Возвращает произведение по title_id из URL."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает все отзывы к конкретному произведению."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """При создании отзыва сохраняет автора и произведение."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_review(self):
        """Возвращает отзыв по review_id из URL."""
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        """Возвращает все комментарии к конкретному отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий с автором и привязкой к отзыву."""
        serializer.save(author=self.request.user, review=self.get_review())


class YamdbUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = YamdbUserSerializer
    lookup_field = 'username'
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username']
    pagination_class = pagination.PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        serializer_class=MeUserSerializer
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = MeUserSerializer(instance=request.user)
            return Response(serializer.data)
        else:
            serializer = MeUserSerializer(
                instance=request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CreateUser(generics.CreateAPIView):
    """
    Представление для первого этапа регистрации пользователей.
    Принимает email и username, проверяет валидность данных.
    Отправляет письмо с кодом подтверждения (confirmation_code) на адрес email.
    """

    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Создает пользователя, если его нет в базе данных.
        Отправляет письмо с кодом подтверждения.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )


class TokenObtainPairView(generics.CreateAPIView):
    """
    Получает username и confirmation_code, проверяет валидность данных.
    В ответ на запрос отправляет token (JWT-токен).
    """

    serializer_class = TokenObtainSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        try:
            user = User.objects.get(username=username)
            access_token = AccessToken.for_user(user)

            return Response({
                'access': str(access_token),
            })

        except Exception:
            return Response(
                {'error': 'Ошибка при получении токена'},
                status=status.HTTP_400_BAD_REQUEST
            )
