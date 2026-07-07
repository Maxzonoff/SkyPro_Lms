from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CASCADE

from materials.models import Course, Lesson
from users.constants import PaymentMethod


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class Town(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    phone_number = models.CharField(max_length=12, blank=True, null=True)
    town = models.ForeignKey(Town, on_delete=models.CASCADE, blank=True, null=True)
    avatar = models.ImageField(upload_to="user/avatars/", blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="payments")
    payment_date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(
        Course, on_delete=CASCADE, blank=True, null=True, help_text="Выберите курс"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=CASCADE, blank=True, null=True, help_text="Выберите урок"
    )
    payment_amount = models.DecimalField(
        decimal_places=2, max_digits=8, validators=[MinValueValidator(0)]
    )
    payment_method = models.CharField(
        max_length=15,
        choices=PaymentMethod.CHOICES,
        default=PaymentMethod.BANK_TRANSFER,
    )

    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    payment_link = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, default="pending")

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"
