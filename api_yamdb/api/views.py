from django.shortcuts import get_object_or_404
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
    IsAdminOrReadOnly,
    OnlyAdmin,
    OnlyOwnAccount,
    OwnerOrReadOnlyList,
    ReadOnly, AdminOrModerator,
)
from .serializers import (
    AuthSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewsSerializer,
    TitleSerializer,
    # TitleSerializerList,
    TokenDataSerializer,
    UsersSerializer, ReviewsSerializerPost,
)


class AuthViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = AuthSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


@api_view(["POST", ])
def get_jwt_token(request):
    serializer = TokenDataSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.get(username=serializer.validated_data["username"])
        user.is_active = True
        user.save()
        token = RefreshToken.for_user(user)
        return Response(
            {"token": str(token.access_token)}, status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        # user = User.objects.get(username=self.request.user.username)

        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # if request.method == "PATCH":
        #     serializer = self.get_serializer(
        #         user, data=request.data, partial=True
        #     )
        #     if serializer.is_valid():
        #         if "role" in serializer.validated_data:
        #             if user.role == "user":
        #                 serializer.validated_data["role"] = "user"
        #         serializer.save()
        #         return Response(serializer.data, status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if "role" in serializer.validated_data:
                serializer.validated_data["role"] = request.user.role
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (OwnerOrReadOnlyList | AdminOrModerator,)
    pagination_class = pagination.PageNumberPagination


    def get_serializer_class(self):
        if self.action == "create":
            return ReviewsSerializerPost
        return ReviewsSerializer

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))


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

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        return super().get_permissions()

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
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ("name",)


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
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        queryset = Title.objects.all()
        genre_slug = self.request.query_params.get("genre")
        category_slug = self.request.query_params.get("category")
        name_in_query = self.request.query_params.get("name")
        year_in_query = self.request.query_params.get("year")

        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        elif category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        elif name_in_query:
            queryset = queryset.filter(name__contains=name_in_query)
        elif year_in_query:
            queryset = queryset.filter(year=year_in_query)
        return queryset

