from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class YamdbUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Некорректное имя пользователя.',
            code='invalid_username'
        )],
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
