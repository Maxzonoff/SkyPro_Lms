from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Заполняет таблицу Payment тестовыми данными"

    def handle(self, *args, **options):
        # Берём первого пользователя (или создаём, если нет)
        user, _ = User.objects.get_or_create(
            email="test@test.ru", defaults={"password": "1234"}
        )

        # Берём существующие курсы и уроки
        course1 = Course.objects.first()
        course2 = Course.objects.all()[1] if Course.objects.count() > 1 else None
        lesson1 = Lesson.objects.first()
        lesson2 = Lesson.objects.all()[1] if Lesson.objects.count() > 1 else None

        if not course1 or not lesson1:
            self.stdout.write(self.style.ERROR("Сначала создай курсы и уроки!"))
            return

        # Создаём платежи
        payments = [
            Payment(
                user=user,
                course=course1,
                lesson=None,
                payment_amount=15000.00,
                payment_method="bank_transfer",
            ),
            Payment(
                user=user,
                course=None,
                lesson=lesson1,
                payment_amount=3000.00,
                payment_method="cash",
            ),
            Payment(
                user=user,
                course=course2,
                lesson=None,
                payment_amount=20000.00,
                payment_method="bank_transfer",
            ),
            Payment(
                user=user,
                course=None,
                lesson=lesson2,
                payment_amount=5000.00,
                payment_method="cash",
            ),
        ]

        for payment in payments:
            payment.save()
            self.stdout.write(self.style.SUCCESS(f"Создан платеж: {payment}"))

        self.stdout.write(self.style.SUCCESS("Готово!"))
