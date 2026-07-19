from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return

    subscriptions = Subscription.objects.filter(course=course)
    recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

    if not recipient_list:
        return

    subject = f"Обновление курса: {course.title}"
    message = (
        f"Здравствуйте!\n\n"
        f"Курс «{course.title}» был обновлён.\n"
        f"Зайдите на платформу, чтобы посмотреть новые материалы.\n\n"
        f"С уважением,\nКоманда SkyPro LMS"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )


@shared_task
def check_and_send_course_update(course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return

    now = timezone.now()
    last_update = course.updated_at
    four_hours_ago = now - timedelta(hours=4)

    if last_update < four_hours_ago:
        send_course_update_email.delay(course_id)
