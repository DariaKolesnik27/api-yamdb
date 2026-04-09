import uuid

from django.core.mail import send_mail
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, generics, mixins, pagination, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from users.models import YamdbUser
from api.filters import TitleFilter
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    # TitleWriteSerializer,
    # TitleReadSerializer,
    TitleSerializer,
    ReviewSerializer,
    TokenObtainSerializer,
    YamdbUserSerializer
)
from api.permissions import IsAdminOrReadOnly, IsAuthorModeratorAdmin, IsOwnerOrAdmin


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly, )


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly, )


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    # def get_serializer_class(self):
    #     if self.action in ('list', 'retrieve'):
    #         return TitleReadSerializer
    #     return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdmin,)
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
    permission_classes = (IsAuthorModeratorAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_review(self):
        """Возвращает отзыв по review_id из URL."""
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Возвращает все комментарии к конкретному отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий с автором и привязкой к отзыву."""
        serializer.save(author=self.request.user, review=self.get_review())


class YamdbUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = YamdbUser.objects.all()
    serializer_class = YamdbUserSerializer
    lookup_field = 'username'
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username']
    pagination_class = pagination.PageNumberPagination

    def get_object(self):
        username = self.kwargs['username']
        if username == 'me':
            if not self.request.user.is_authenticated:
                raise exceptions.NotAuthenticated()
            return self.request.user

        obj = get_object_or_404(
            self.get_queryset(),
            username=username
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = self.kwargs['username']
        if username == 'me':
            return Response(status=405)
        self.perform_destroy(instance)
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=405)
        if (
            self.kwargs['username'] == 'me'
            and 'role' in request.data
            and not request.user.is_staff
        ):
            return Response(
                'Изменение роли запрещено для данного пользователя.',
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        if email and YamdbUser.objects.filter(email=email).exists():
            return Response(
                {'email': ['Пользователь с таким email уже существует.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if username and YamdbUser.objects.filter(username=username).exists():
            return Response(
                'Пользователь с таким username уже существует.',
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CreateUser(generics.CreateAPIView):
    """
    Представление для первого этапа регистрации пользователей.
    Принимает email и username, проверяет валидность данных.
    Отправляет письмо с кодом подтверждения (confirmation_code) на адрес email.
    """

    serializer_class = YamdbUserSerializer
    permission_classes = [AllowAny]

    def generate_confirmation_code(self):
        """Генерирует UUID и обрезает до нужной длины."""
        return str(uuid.uuid4()).replace('-', '')[:12]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        try:
            code = self.generate_confirmation_code()
            user_by_email = YamdbUser.objects.filter(email=email).first()
            user_by_username = (
                YamdbUser.objects.filter(username=username).first()
            )

            if user_by_email and not user_by_username:
                return Response(
                    {'error': 'Пользователь с таким email уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif user_by_username and not user_by_email:
                return Response(
                    {'error': 'Пользователь с таким username уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif user_by_email and user_by_username:
                if user_by_email == user_by_username:
                    user_by_email.confirmation_code = code
                    user_by_email.save()
                else:
                    return Response(
                        'Username и email принадлежат разным пользователям',
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                YamdbUser.objects.create(
                    email=email,
                    username=username,
                    confirmation_code=code
                )
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
            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK
            )
        except Exception:
            raise ValidationError(
                {'Не удалось отправить письмо с кодом подтверждения.'}
            )


class TokenObtainPairView(generics.CreateAPIView):
    """В ответ на запрос отправляет token (JWT-токен)."""

    serializer_class = TokenObtainSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        if not username or not confirmation_code:
            return Response(
                'username и confirmation_code обязательны',
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = YamdbUser.objects.get(username=username)
            if user.confirmation_code != confirmation_code:
                return Response(
                    'Неверный код подтверждения',
                    status=status.HTTP_400_BAD_REQUEST
                )

            access_token = AccessToken.for_user(user)

            return Response({
                'access': str(access_token),
            })

        except YamdbUser.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {'error': 'Ошибка при получении токена'},
                status=status.HTTP_400_BAD_REQUEST
            )
