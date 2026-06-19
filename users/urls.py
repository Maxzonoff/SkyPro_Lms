from django.urls import path
from rest_framework.permissions import AllowAny

from users.views import (
    UserProfileView,
    PaymentListAPIView,
    UsersCreateAPIView,
    UsersListAPIView,
    UsersRetrieveAPIView,
    UsersUpdateAPIView,
    UsersDestroyAPIView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "users"

urlpatterns = [
    path("<int:pk>/profile/", UserProfileView.as_view(), name="profile_update"),
    path("", UsersListAPIView.as_view(), name="users_list"),
    path("<int:pk>/", UsersRetrieveAPIView.as_view(), name="users_retrieve"),
    path("<int:pk>/update/", UsersUpdateAPIView.as_view(), name="users_update"),
    path("<int:pk>/delete/", UsersDestroyAPIView.as_view(), name="users_delete"),
    path("register/", UsersCreateAPIView.as_view(), name="register"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
    path("payments/", PaymentListAPIView.as_view(), name="payments_list"),
]
