"""Модели для приложения reviews."""
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from reviews.validators import validate_year


STR_LIMIT = 20


class Category(models.Model):
    """Модель для категорий произведений."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг категории',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_LIMIT]


class Genre(models.Model):
    """Модель для жанров произведений."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг жанра',
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_LIMIT]


class Title(models.Model):
    """Модель для произведений."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Год выпуска',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('year',)

    def __str__(self):
        return self.name[:STR_LIMIT]


class Review(models.Model):
    """Модель для отзывов на произведения."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    author = models.ForeignKey(
        'users.YamdbUser',
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва',
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации отзыва',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            ),
        )

    def __str__(self):
        return self.text[:STR_LIMIT]


class Comment(models.Model):
    """Модель для комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    author = models.ForeignKey(
        'users.YamdbUser',
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:STR_LIMIT]
