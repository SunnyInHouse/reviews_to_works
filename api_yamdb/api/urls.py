from rest_framework import routers

from django.urls import include, path

from .views import GenreViewSet, CategoryViewSet, TitleViewSet


router = routers.DefaultRouter()
router.register(r'api/v1/genres', GenreViewSet)
router.register(r'api/v1/categories', CategoryViewSet)
router.register(r'api/v1/titles', TitleViewSet)

urlpatterns = [
    path('', include(router.urls))
]
