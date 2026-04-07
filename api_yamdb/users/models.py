from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class YamdbUser(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=(
                'Поле обязательно для заполнения. '
                'Может содержать только буквы, цыфры и символы @/./+/-/_.'
            ),
            code='invalid_username'
        )],
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Почта'
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    bio = models.TextField(verbose_name='Биография пользователя')
    role = models.CharField(max_length=100, default='user')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
