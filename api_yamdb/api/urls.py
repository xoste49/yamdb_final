from .views import (
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
    # UserMeView,
    UserViewSet,
    CommentViewSet,
    ReviewViewSet,
    get_token,
    get_confirmation,
)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView


router = DefaultRouter()

router.register('users', UserViewSet, basename='User')

# (GET, POST) /titles/{title_id}/reviews/
# (GET, PATCH, DELETE) /titles/{title_id}/reviews/{review_id}/
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

# (GET, POST) /titles/{title_id}/reviews/{review_id}/comments/
# (GET, PATCH, DELETE)
#               /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

router.register(r'^categories', CategoryViewSet)
router.register(r'^genres', GenreViewSet)
router.register(r'^titles', TitleViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]

urlpatterns += [
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(
        'v1/auth/token/',
        get_token,
        name='get_token'
    ),
    path(
        'v1/auth/email/',
        get_confirmation,
        name='email_confirmation'
    ),
    path(
        'v1/auth/admin_token/',
        TokenObtainPairView.as_view(),
        name='admin_token'
    ),
]
