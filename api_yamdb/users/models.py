import re

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


MAX_NAMES_LENGTH = 150
EMAIL_LENGTH = 254
CODE_LENGTH = 12


def valid_username(username):
    pattern = r'[\w.@+-]'
    invalid_chars = re.sub(pattern, '', username)
    if username.lower() == 'me':
        raise ValidationError('Нельзя использовать "me" как имя пользователя.')
    elif invalid_chars:
        unique_chars = ' '.join(set(invalid_chars))
        raise ValidationError(
            'Использованы недопустимые символы в имени пользователя: '
            f'{unique_chars}. Поле может содержать только буквы, цифры и '
            'символы @/./+/-/_.'
        )


class YamdbUser(AbstractUser):
    """Модель пользователя."""

    class Roles(models.TextChoices):
        ROLE_USER = 'user', _('user')
        ROLE_MODERATOR = 'moderator', _('moderator')
        ROLE_ADMIN = 'admin', _('admin')

    username = models.CharField(
        max_length=MAX_NAMES_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(), valid_username
        ],
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_LENGTH,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=MAX_NAMES_LENGTH,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_NAMES_LENGTH,
        blank=True,
        verbose_name='Фамилия'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография пользователя'
    )
    role = models.CharField(
        max_length=max(map(len, [role[1] for role in Roles.choices])),
        choices=Roles.choices,
        default=Roles.ROLE_USER,
        blank=True,
    )
    confirmation_code = models.CharField(
        max_length=CODE_LENGTH,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return (
            self.is_superuser
            or self.role == self.Roles.ROLE_ADMIN.value
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == self.Roles.ROLE_MODERATOR.value

    def __str__(self):
        return self.username
