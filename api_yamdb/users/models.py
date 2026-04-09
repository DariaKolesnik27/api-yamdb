from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


MAX_NAMES_LENGTH = 150
EMAIL_LENGTH = 254
CODE_LENGTH = 12
ROLE_USER = 'user'
ROLE_MODERATOR = 'moderator'
ROLE_ADMIN = 'admin'

ROLES = [
    (ROLE_USER, 'Пользователь'),
    (ROLE_MODERATOR, 'Модератор'),
    (ROLE_ADMIN, 'Администратор'),
]


class YamdbUser(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=MAX_NAMES_LENGTH,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=(
                'Поле обязательно для заполнения. '
                'Может содержать только буквы, цифры и символы @/./+/-/_.'
            ),
            code='invalid_username'
        )],
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_LENGTH,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=MAX_NAMES_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_NAMES_LENGTH,
        verbose_name='Фамилия'
    )
    bio = models.TextField(verbose_name='Биография пользователя')
    role = models.CharField(max_length=20, choices=ROLES, default=ROLE_USER)
    confirmation_code = models.CharField(
        max_length=CODE_LENGTH,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_superuser or self.role == ROLE_ADMIN

    def __str__(self):
        return self.username
