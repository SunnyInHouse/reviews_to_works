from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    mixins,
    pagination,
    permissions as perm,
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
    Admin,
    OwnAccount,
    Owner,
    ReadOnly,
)
from .serializers import (
    AuthSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewsSerializer,
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
    
    def perform_create(self, serializer):
        serializer.save()
        user = User.objects.get(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        # отправляем письмо пользователю
        send_mail(
            subject="Код подтверждения регистрации",
            message=(
                f"Код подтверждения регистрации ниже \n "
                f"{confirmation_code}. \n Имя пользователя "
                f"{serializer.validated_data['username']}"
            ),
            from_email=None,
            recipient_list=[
                serializer.validated_data["email"],
            ],
        )

@api_view(["POST", ])
def get_jwt_token(request):
    serializer = TokenDataSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )
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
    permission_classes = (perm.IsAuthenticated&Admin,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("=username",)

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=(OwnAccount,),
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
    permission_classes = (Owner|AdminOrModerator|ReadOnly,)
    pagination_class = pagination.PageNumberPagination

    @property
    def _title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        title = self._title
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self._title
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (Owner|AdminOrModerator|ReadOnly,)
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
    permission_classes = (perm.IsAuthenticated&Admin|ReadOnly,)
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
    permission_classes = (perm.IsAuthenticated&Admin|ReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (perm.IsAuthenticated&Admin|ReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
