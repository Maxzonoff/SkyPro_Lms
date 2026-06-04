from rest_framework import serializers

from materials.models import Course, Lesson
from users.models import User, Payment


class CourseShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "title")


class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title")


class PaymentSerializer(serializers.ModelSerializer):
    course = CourseShortSerializer(read_only=True)
    lesson = LessonShortSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "payment_date", "payment_amount", "payment_method", "course", "lesson")

    def validate(self, data):
        course = data.get("course")
        lesson = data.get("lesson")

        if not course and not lesson:
            raise serializers.ValidationError("Укажите курс или урок")
        if course and lesson:
            raise serializers.ValidationError("Укажите только курс или только урок")

        return data


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "town",
            "avatar",
            "first_name",
            "last_name",
            "payments",
        ]
