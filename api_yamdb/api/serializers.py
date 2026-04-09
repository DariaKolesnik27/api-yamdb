import re

from rest_framework import serializers, status

from users.models import YamdbUser


class YamdbUserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователями."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    role = serializers.ChoiceField(
        choices=['user', 'moderator', 'admin'],
        required=False,
        default='user'
    )

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Username должен содержать только буквы, '
                'цифры и символы @/./+/-/_.'
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина username не должна превышать 150 символов.'
            )
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                'Длина email не должна превышать 254 символа.'
            )
        return value

    class Meta:
        model = YamdbUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
            'confirmation_code'
        )
        extra_kwargs = {
            'confirmation_code': {'required': False, 'write_only': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'bio': {'required': False, 'allow_blank': True}
        }


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для работы с токенами."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        try:
            user = YamdbUser.objects.get(username=username)
        except YamdbUser.DoesNotExist:
            raise serializers.ValidationError(
                {'username': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )
        data['user'] = user
        return data
