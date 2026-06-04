from django.urls import path
from users.views import UserProfileView, PaymentListAPIView

app_name = "users"

urlpatterns = [
    path("<int:pk>/profile/", UserProfileView.as_view(), name="profile_update"),
    path("payments/", PaymentListAPIView.as_view(), name="payments_list"),
]
