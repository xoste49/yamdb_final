import binascii
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilterSet
from .models import (
    Confirmation,
    Review,
    Title,
    Category,
    Genre
)
from .paginations import StandardResultsSetPagination
from .permissions import (
    AuthorPermisssion,
    AdminPermission,
    AdminOrReadOnly,
    ModeratorPermission
)
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    TokenSerializer,
    WriteTitleSerializer,
    ReadTitleSerializer,
    CategorySerializer,
    GenreSerializer,
    ConfirmationSerializer,
)
from .viewsets import CustomModelViewSet

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Работа с отзывами на произведения
    """
    serializer_class = ReviewSerializer
    permission_classes = (
        AuthorPermisssion | AdminPermission | ModeratorPermission,
    )
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Работа с комментариями к отзывам.
    """
    serializer_class = CommentSerializer
    permission_classes = (
        AuthorPermisssion | AdminPermission | ModeratorPermission,
    )
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminPermission,)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['PATCH', 'GET'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    recieved_key = serializer.validated_data['confirmation']
    confirmation = get_object_or_404(Confirmation, email=email)
    stored_key = confirmation.key
    if recieved_key == stored_key:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'email': email,
                'role': 'user'
            }
        )
        token = RefreshToken.for_user(user)
        confirmation.delete()
        return Response({'token': str(token.access_token)})
    return Response('Something is wrong')


@api_view(['POST'])
def get_confirmation(request):
    serializer = ConfirmationSerializer(data=request.data)
    key = binascii.hexlify(os.urandom(20)).decode()
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    Confirmation.objects.update_or_create(
        email=email,
        defaults={
            'email': email,
            'key': key
        }
    )
    send_mail(
        subject='Confirmation',
        message=key,
        from_email=settings.ADMIN_EMAIL,
        recipient_list=[email]
    )
    return Response(
        f'Код подтверждения отправлен на адрес {email}',
        status=status.HTTP_200_OK
    )


class CategoryViewSet(CustomModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    http_method_names = ['get', 'post', 'delete']
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilterSet
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return WriteTitleSerializer
        return ReadTitleSerializer


class GenreViewSet(CustomModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    http_method_names = ['get', 'post', 'delete']
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrReadOnly,)
