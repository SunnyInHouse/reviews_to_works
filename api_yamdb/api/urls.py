from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuthViewSet,
    CategoryViewSet,
    CommentsViewSet,
    GenreViewSet,
    ReviewsViewSet,
    TitleViewSet,
    UsersViewSet,
    get_jwt_token,
)

router1 = DefaultRouter()

router1.register(
    r"v1/auth/signup",
    AuthViewSet,
    basename="signup",
)
router1.register(
    r"v1/users",
    UsersViewSet,
    basename="users",
)
router1.register(
    r"v1/titles/(?P<title_id>\d+)/reviews",
    ReviewsViewSet,
    basename="review",
)
router1.register(
    r"v1/titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentsViewSet,
    basename="comment",
)
router1.register(
    r"v1/genres",
    GenreViewSet,
    basename="genre",
)
router1.register(
    r"v1/categories",
    CategoryViewSet,
    basename="category",
)
router1.register(
    r"v1/titles",
    TitleViewSet,
    basename="title",
)

urlpatterns = [
    path("v1/auth/token/", get_jwt_token),
    path("", include(router1.urls)),
]
