from django.urls import include, path
from rest_framework import routers

from .views import ReviewsViewSet, CommentsViewSet

router = routers.DefaultRouter()
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewsViewSet, basename="review"
)

router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentsViewSet,
    basename="comment"
)

urlpatterns = [
    path("v1/", include(router.urls))
]
