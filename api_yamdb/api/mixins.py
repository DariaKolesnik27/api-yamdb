from rest_framework import (
    filters, mixins, viewsets
)

from api.permissions import IsAdminOrReadOnly


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
