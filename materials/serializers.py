from drf_spectacular.utils import extend_schema_field
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
            "price",
            "lesson_count",
            "lessons",
            "owner",
            "is_subscribed",
        )
        read_only_fields = ("owner",)

    @extend_schema_field(int)
    def get_lesson_count(self, course):
        return course.lessons.count()

    @extend_schema_field(bool)
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


class PaymentCreateSerializer(serializers.Serializer):
    """
    Сериализатор для создания платежа.
    Пользователь передаёт ID курса, мы создаём всё остальное.
    """

    course_id = serializers.IntegerField(
        help_text="ID курса, который хочет оплатить пользователь"
    )


class PaymentResponseSerializer(serializers.Serializer):
    """
    Ответ при создании платежа — ссылка на оплату в Stripe.
    """

    payment_id = serializers.IntegerField(help_text="ID платежа в нашей системе")
    payment_link = serializers.URLField(help_text="Ссылка на оплату в Stripe")
    session_id = serializers.CharField(help_text="ID сессии в Stripe")


class PaymentStatusSerializer(serializers.Serializer):
    """
    Ответ при проверке статуса платежа.
    """

    status = serializers.CharField(
        help_text="Статус в нашей системе (pending/paid/cancelled)"
    )
    stripe_status = serializers.CharField(help_text="Статус сессии в Stripe")
    payment_status = serializers.CharField(
        help_text="Статус оплаты в Stripe (unpaid/paid)"
    )


class SubscriptionActionSerializer(serializers.Serializer):
    """
    Для подписки/отписки — пользователь передаёт course_id.
    """

    course = serializers.IntegerField(help_text="ID курса для подписки/отписки")


class SubscriptionActionResponseSerializer(serializers.Serializer):
    """
    Ответ при подписке/отписке.
    """

    message = serializers.CharField(help_text="Результат действия")
