from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.ru", password="test")
        self.course = Course.objects.create(
            title="Python", description="Курс по Python", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Урок 1",
            description="Описание",
            video_url="https://www.youtube.com/watch?v=abc",
            course=self.course,
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_lesson_create(self):
        """Тест создания урока"""
        url = reverse("materials:lessons_create")
        data = {
            "title": "Урок 2",
            "description": "Новый урок",
            "video_url": "https://www.youtube.com/watch?v=xyz",
            "course": self.course.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_bad_url(self):
        """Тест: нельзя добавить ссылку не на YouTube"""
        url = reverse("materials:lessons_create")
        data = {
            "title": "Урок 2",
            "description": "Новый урок",
            "video_url": "https://stepik.org/lesson/123",
            "course": self.course.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_list(self):
        """Тест списка уроков"""
        url = reverse("materials:lessons_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.ru", password="testpass")
        self.course = Course.objects.create(
            title="Python", description="Курс", owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_subscribe(self):
        """Тест подписки"""
        url = reverse("materials:subscribe")
        response = self.client.post(url, {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "подписка добавлена")
        self.assertEqual(Subscription.objects.count(), 1)

    def test_unsubscribe(self):
        """Тест отписки"""
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse("materials:subscribe")
        response = self.client.post(url, {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "подписка удалена")
        self.assertEqual(Subscription.objects.count(), 0)
