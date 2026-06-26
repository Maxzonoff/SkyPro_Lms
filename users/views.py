import stripe
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
)
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, Payment
from users.permissions import IsOwner
from users.serializers import (
    UserSerializer,
    PaymentSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)


class UserProfileView(RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля.
    - GET: любой авторизованный может смотреть любой профиль (общая инфа)
    - PATCH/PUT: только владелец может редактировать свой профиль
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserProfileUpdateSerializer  # Редактирование
        return UserProfileSerializer  # Просмотр

    def get_object(self):
        # Получаем пользователя по pk из URL
        obj = super().get_object()

        # Для редактирования — проверяем, что это свой профиль
        if self.request.method in ["PUT", "PATCH"]:
            if obj != self.request.user:
                raise PermissionDenied("Вы можете редактировать только свой профиль")

        return obj


class UsersCreateAPIView(CreateAPIView):
    """Регистрация — доступна всем"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UsersListAPIView(ListAPIView):
    """Список пользователей — только авторизованным"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UsersRetrieveAPIView(RetrieveAPIView):
    """Просмотр пользователя — только авторизованным"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UsersUpdateAPIView(UpdateAPIView):
    """Обновление пользователя — только авторизованным"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UsersDestroyAPIView(DestroyAPIView):
    """Удаление пользователя — только авторизованным"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserProfileAPIView(RetrieveAPIView):
    """Просмотр любого профиля"""

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class UserProfileUpdateAPIView(UpdateAPIView):
    """Редактирование только своего профиля"""

    serializer_class = UserProfileUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class PaymentListAPIView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["payment_date"]
    permission_classes = [IsAuthenticated]
