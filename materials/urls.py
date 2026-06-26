from django.urls import path
from rest_framework.routers import DefaultRouter

from materials.views import (
    CourseViewSet,
    LessonCreateApiView,
    LessonListApiView,
    LessonUpdateApiView,
    LessonRetrieveApiView,
    LessonDestroyApiView,
    SubscriptionAPIView,
    CoursePaymentAPIView,
    PaymentStatusAPIView,
)

app_name = "materials"

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/", LessonListApiView.as_view(), name="lessons_list"),
    path("lessons/<int:pk>/", LessonRetrieveApiView.as_view(), name="lessons_retrieve"),
    path("lessons/create/", LessonCreateApiView.as_view(), name="lessons_create"),
    path(
        "lessons/<int:pk>/delete/",
        LessonDestroyApiView.as_view(),
        name="lessons_delete",
    ),
    path(
        "lessons/<int:pk>/update/", LessonUpdateApiView.as_view(), name="lessons_update"
    ),
    path("subscribe/", SubscriptionAPIView.as_view(), name="subscribe"),
    path("courses/<int:pk>/pay/", CoursePaymentAPIView.as_view(), name="course_pay"),
    path(
        "payments/<int:pk>/status/",
        PaymentStatusAPIView.as_view(),
        name="payment_status",
    ),
]

urlpatterns += router.urls
