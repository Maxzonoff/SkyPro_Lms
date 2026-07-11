from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
)
from django.shortcuts import get_object_or_404

from materials.models import Lesson, Course, Subscription
from materials.paginators import CoursePaginator, LessonPaginator
from materials.serializers import (
    CourseSerializer,
    LessonSerializer,
    PaymentResponseSerializer,
    PaymentStatusSerializer,
    SubscriptionActionResponseSerializer,
)
from users.constants import PaymentMethod
from users.models import Payment
from users.permissions import IsModer, IsOwner

from materials.services import StripeService

from .tasks import check_and_send_course_update


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moders").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_update(self, serializer):
        instance = serializer.save()
        check_and_send_course_update.delay(instance.pk)


class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moders").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moders").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer, IsOwner]


@extend_schema(
    request=None,
    responses={200: SubscriptionActionResponseSerializer},
    description="Подписка или отписка от курса. Передай course_id в теле запроса.",
)
class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course")
        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        return Response({"message": message})


@extend_schema(
    request=None,
    responses={200: PaymentResponseSerializer},
    description="Создаёт продукт, цену и сессию оплаты в Stripe. Возвращает ссылку на оплату.",
)
class CoursePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        user = request.user

        if Payment.objects.filter(user=user, course=course, status="paid").exists():
            return Response(
                {"detail": "Курс уже оплачен"}, status=status.HTTP_400_BAD_REQUEST
            )

        course_price = getattr(course, "price", 1000)
        amount_in_kopecks = int(course_price * 100)

        product = StripeService.create_product(
            name=course.title, description=course.description[:255]
        )

        price = StripeService.create_price(
            product_id=product.id, amount=amount_in_kopecks
        )

        success_url = "http://127.0.0.1:8000/"
        cancel_url = "http://127.0.0.1:8000/"

        session = StripeService.create_checkout_session(
            price_id=price.id, success_url=success_url, cancel_url=cancel_url
        )

        payment = Payment.objects.create(
            user=user,
            course=course,
            payment_amount=course_price,
            payment_method=PaymentMethod.BANK_TRANSFER,
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            stripe_session_id=session.id,
            payment_link=session.url,
            status="pending",
        )

        return Response(
            {
                "payment_id": payment.id,
                "payment_link": session.url,
                "session_id": session.id,
            }
        )


@extend_schema(
    request=None,
    responses={200: PaymentStatusSerializer},
    description="Проверяет статус платежа в Stripe и синхронизирует с нашей БД.",
)
class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, id=pk, user=request.user)

        if not payment.stripe_session_id:
            return Response({"status": payment.status})

        import stripe

        session = stripe.checkout.Session.retrieve(payment.stripe_session_id)

        if session.payment_status == "paid":
            payment.status = "paid"
        elif session.status == "expired":
            payment.status = "cancelled"
        payment.save()

        return Response(
            {
                "status": payment.status,
                "stripe_status": session.status,
                "payment_status": session.payment_status,
            }
        )