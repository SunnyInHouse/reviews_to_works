from rest_framework import filters, mixins, pagination, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from .permissions import OnlyAdmin, OnlyOwnAccount
from .serializers import AuthSerializer, TokenDataSerializer, UsersSerializer


class AuthViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = AuthSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK,
            headers=headers
        )


@api_view(['POST', ])
def get_jwt_token(request):
    serializer = TokenDataSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.get(username=serializer.validated_data['username'])
        user.is_active = True
        user.save()
        token = RefreshToken.for_user(user)
        return Response(
            {'token': str(token.access_token)},
            status=status.HTTP_200_OK
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'username'
    permission_classes = (OnlyAdmin, )
    authentication_classes = (JWTAuthentication,)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('=username',)
    pagination_class = pagination.PageNumberPagination

    @action(
        detail=True,
        methods=['get', 'patch'],
        permission_classes=(OnlyOwnAccount,)
    )
    def me(self, request):
        user = User.objects.get(username=self.request.user.username)

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                if 'role' in serializer.validated_data:
                    if user.role == 'user':
                        serializer.validated_data['role'] = 'user'
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
