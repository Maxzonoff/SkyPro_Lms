from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import User


@shared_task
def block_inactive_users():
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)

    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True,
    )

    count = inactive_users.update(is_active=False)
    return f"Blocked {count} inactive users"
