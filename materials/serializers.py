from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from materials.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "preview",
            "description",
            "video_url",
            "course",
        )


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = SerializerMethodField()
    lessons = LessonSerializer(read_only=True, many=True)

    class Meta:
        model = Course
        fields = ("id", "title", "description", "lesson_count", "lessons")

    def get_lesson_count(self, course):
        return course.lessons.count()
