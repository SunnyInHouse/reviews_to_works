from django.shortcuts import get_object_or_404

from rest_framework import viewsets

from .models import Titles, Reviews
from .permissions import OwnerOrReadOnlyList, ReadOnly
from .serializers import ReviewsSerializer, CommentSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (OwnerOrReadOnlyList,)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        print('self.kwargs.get("title_id") = ', self.kwargs.get("title_id"))
        title = get_object_or_404(Titles, pk=self.kwargs.get("title_id"))
        print("title = ", title)
        return title.reviews

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (OwnerOrReadOnlyList,)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        review = get_object_or_404(
            Reviews,
            pk=self.kwargs.get("reviews_id"),
            title__pk=self.kwargs.get("title_id")
        )
        return review.comment

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
