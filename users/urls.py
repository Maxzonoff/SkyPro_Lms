from django.urls import path
from users.views import UserUpdateView

app_name = "users"

urlpatterns = [
    path("<int:pk>/profile/", UserUpdateView.as_view(), name="profile_update"),
]
