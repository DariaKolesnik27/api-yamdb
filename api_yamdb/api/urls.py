from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CreateUser, TokenObtainPairView, YamdbUserViewSet


v1_router = DefaultRouter()
v1_router.register('users', YamdbUserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/signup/', CreateUser.as_view(), name='create_user'),
    path(
        'v1/auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
]
