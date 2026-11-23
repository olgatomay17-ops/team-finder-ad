from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from projects.models import Project, ProjectMembership

from .models import User


class UserModelTest(TestCase):
    def test_avatar_generation(self):
        """Проверяем, что при создании пользователя генерируется аватар."""
        user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            name="Иван",
            surname="Иванов",
            phone="1234567890",
        )
        self.assertIsNotNone(user.avatar)
        self.assertTrue(user.avatar.name.endswith(".png"))

    def test_str_method(self):
        """Проверяем строковое представление."""
        user = User(email="test@example.com", name="Иван", surname="Иванов")
        self.assertEqual(str(user), "Иван Иванов")


class UserViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            name="Иван",
            surname="Иванов",
            phone="1234567890",
        )

    def test_register_page(self):
        """Проверяем доступность страницы регистрации."""
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/register.html")

    def test_login_and_redirect(self):
        """Проверяем вход и перенаправление после него."""
        # Пытаемся войти
        response = self.client.post(
            reverse("users:login"), {"email": "test@example.com", "password": "password123"}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_page(self):
        """Проверяем страницу профиля."""
        response = self.client.get(reverse("users:detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Иван Иванов")


class UserFilterTest(TestCase):

    def setUp(self):
        # Текущий пользователь
        self.current_user = User.objects.create_user(
            email="current@example.com",
            password="password123",
            name="Текущий",
            surname="Пользователь",
            phone="111",
        )

        # Автор избранного проекта
        self.favorite_owner = User.objects.create_user(
            email="favorite@example.com",
            password="password123",
            name="Автор",
            surname="Избранного",
            phone="222",
        )

        # Автор проекта, в котором участвует текущий пользователь
        self.participating_owner = User.objects.create_user(
            email="participating@example.com",
            password="password123",
            name="Автор",
            surname="Участия",
            phone="333",
        )

        # Пользователь, которому нравятся проекты текущего пользователя
        self.interested_user = User.objects.create_user(
            email="interested@example.com",
            password="password123",
            name="Заинтересованный",
            surname="Пользователь",
            phone="444",
        )

        # Участник собственного проекта
        self.project_participant = User.objects.create_user(
            email="participant@example.com",
            password="password123",
            name="Участник",
            surname="Проекта",
            phone="555",
        )

        # Создаём проекты
        self.favorite_project = Project.objects.create(
            name="Избранный проект", description="Тест", owner=self.favorite_owner
        )

        self.participating_project = Project.objects.create(
            name="Проект с участием", description="Тест", owner=self.participating_owner
        )

        self.own_project = Project.objects.create(
            name="Мой проект", description="Тест", owner=self.current_user
        )

        # Текущий пользователь добавляет проект в избранное
        self.current_user.favorites.add(self.favorite_project)

        # Текущий пользователь участвует в чужом проекте
        ProjectMembership.objects.create(user=self.current_user, project=self.participating_project)

        # Другой пользователь добавляет мой проект в избранное
        self.interested_user.favorites.add(self.own_project)

        # Пользователь вступает в мой проект
        ProjectMembership.objects.create(user=self.project_participant, project=self.own_project)

        self.client.login(email="current@example.com", password="password123")

    def test_owners_of_favorite_projects(self):
        response = self.client.get("/users/list/?filter=owners-of-favorite-projects")

        self.assertContains(response, "Избранного")

    def test_owners_of_participating_projects(self):
        response = self.client.get("/users/list/?filter=owners-of-participating-projects")

        self.assertContains(response, "Участия")

    def test_interested_in_my_projects(self):
        response = self.client.get("/users/list/?filter=interested-in-my-projects")

        self.assertContains(response, "Заинтересованный")

    def test_participants_of_my_projects(self):
        response = self.client.get("/users/list/?filter=participants-of-my-projects")

        self.assertContains(response, "Участник")
