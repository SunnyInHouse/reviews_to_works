from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    mixins,
    pagination,
    status,
    viewsets,
)
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from users.models import User

from .permissions import (
    AdminOrModerator,
    OnlyAdmin,
    OnlyOwnAccount,
    OwnerOrReadOnlyList,
    ReadOnly,
)
from .serializers import (
    AuthSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewsSerializer,
    ReviewsSerializerCreate,
    TitleSerializer,
    TokenDataSerializer,
    UsersSerializer,
)
from .filters import TitleFilter


class AuthViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = AuthSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )


@api_view(["POST", ])
def get_jwt_token(request):
    serializer = TokenDataSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    user = get_object_or_404(User, username=request.user.username)
    token = RefreshToken.for_user(user)
    return Response(
        {"token": str(token.access_token)},
        status=status.HTTP_200_OK
    )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = "username"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (OnlyAdmin,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("=username",)

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=(OnlyOwnAccount,),
    )
    def me(self, request):
        user = request.user

        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (OwnerOrReadOnlyList | AdminOrModerator,)
    pagination_class = pagination.PageNumberPagination

    @property
    def _get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        title = self._get_title
        return title.reviews.all()

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewsSerializerCreate
        return ReviewsSerializer

    def perform_create(self, serializer):
        title = self._get_title
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (OwnerOrReadOnlyList | AdminOrModerator,)
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get("review_id"),
            title__pk=self.kwargs.get("title_id"),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get("review_id"),
            title__pk=self.kwargs.get("title_id"),
        )
        serializer.save(author=self.request.user, review=review)


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = "slug"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (OnlyAdmin,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ("name",)

    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        return super().get_permissions()


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (OnlyAdmin,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)

    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        return super().get_permissions()


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (OnlyAdmin,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return (ReadOnly(),)
        return super().get_permissions()
