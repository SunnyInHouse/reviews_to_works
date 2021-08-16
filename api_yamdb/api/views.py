from rest_framework import viewsets, mixins, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Genre, Category, Title
from .serializers import (GenreSerializer, CategorySerializer,
                          TitleSerializer, TitleSerializerList)
from .permissions import IsAdminOrReadOnlyPermission


class GenreViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnlyPermission,)


class CategoryViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnlyPermission,)


class TitleViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('category__slug', 'genre__slug')
    search_fields = ('name', 'year')

    def get_serializer_class(self):
        if self.action == 'list':
            return TitleSerializerList
        if self.action == 'retrive':
            return TitleSerializerList
        return TitleSerializer
