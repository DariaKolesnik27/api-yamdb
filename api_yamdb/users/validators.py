import re

from django.core.exceptions import ValidationError


def valid_username(username):
    pattern = r'^[\w.@+-]+\Z'
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
