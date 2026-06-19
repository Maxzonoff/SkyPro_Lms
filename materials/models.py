from django.db import models
from django.db.models import SET_NULL

from config import settings


class Course(models.Model):
    title = models.CharField(max_length=100)
    preview = models.ImageField(upload_to="course/previews/", blank=True, null=True)
    description = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Укажите владельца курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    title = models.CharField(max_length=100)
    preview = models.ImageField(upload_to="lesson/previews/", blank=True, null=True)
    description = models.TextField()
    video_url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Укажите владельца урока",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
