from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from materials.models import Course, Lesson, Subscription
from materials.validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(validators=[validate_youtube_url])

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "preview",
            "description",
            "video_url",
            "course",
            "owner",
        )
        read_only_fields = ("owner",)


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = SerializerMethodField()
    lessons = LessonSerializer(read_only=True, many=True)
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "lesson_count",
            "lessons",
            "owner",
            "is_subscribed",
        )
        read_only_fields = ("owner",)

    def get_lesson_count(self, course):
        return course.lessons.count()

    def get_is_subscribed(self, course):
        """Проверяем, подписан ли текущий пользователь на курс"""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return course.subscriptions.filter(user=user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("id", "user", "course")
        read_only_fields = ("user",)
