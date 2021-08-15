from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, UsersViewSet, get_jwt_token

router1 = DefaultRouter()
router1.register(r'v1/auth/signup', AuthViewSet)
router1.register(r'v1/users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/auth/token/', get_jwt_token),
    path('', include(router1.urls)),
]
