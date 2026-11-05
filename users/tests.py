from django.test import TestCase
from django.urls import reverse
from .models import User


class UserModelTest(TestCase):
    def test_avatar_generation(self):
        """Проверяем, что при создании пользователя генерируется аватар."""
        user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            name='Иван',
            surname='Иванов',
            phone='1234567890'
        )
        self.assertIsNotNone(user.avatar)
        self.assertTrue(user.avatar.name.endswith('.png'))

    def test_str_method(self):
        """Проверяем строковое представление."""
        user = User(email='test@example.com', name='Иван', surname='Иванов')
        self.assertEqual(str(user), 'Иван Иванов')


class UserViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', password='password123',
            name='Иван', surname='Иванов', phone='1234567890'
        )

    def test_register_page(self):
        """Проверяем доступность страницы регистрации."""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_login_and_redirect(self):
        """Проверяем вход и перенаправление после него."""
        # Пытаемся войти
        response = self.client.post(reverse('users:login'), {
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_profile_page(self):
        """Проверяем страницу профиля."""
        response = self.client.get(
            reverse('users:detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Иван Иванов')
