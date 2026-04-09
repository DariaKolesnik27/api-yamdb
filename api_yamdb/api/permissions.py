from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Разрешает администратору и суперпользователю любые действия, пользователю -
    получение и редактирование своего профиля,
    если запрос отправлен на эндпоинт /users/me/.
    """

    def has_permission(self, request, view):
        if view.action == 'list':
            return (
                request.user.is_authenticated
                and (request.user.role == 'admin' or request.user.is_superuser)
            )
        if request.method in ['DELETE', 'GET', 'PATCH']:
            return request.user.is_authenticated
        return (
            request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        if view.kwargs.get('username') == 'me':
            return obj == request.user
