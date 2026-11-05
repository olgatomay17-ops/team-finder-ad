from django.test import TestCase
from django.urls import reverse
from users.models import User
from .models import Project, ProjectMembership


class ProjectViewTest(TestCase):
    def setUp(self):
        # Создаем двух пользователей: автора и просто зрителя
        self.author = User.objects.create_user(
            email='author@example.com', password='password123',
            name='Автор', surname='Авторов', phone='111'
        )
        self.viewer = User.objects.create_user(
            email='viewer@example.com', password='password123',
            name='Зритель', surname='Зрителей', phone='222'
        )

        # Создаем проект
        self.project = Project.objects.create(
            name='Тестовый проект',
            description='Описание',
            owner=self.author
        )

    def test_project_list_view(self):
        """Проверяем, что главная страница со списком проектов работает."""
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый проект')

    def test_project_edit_by_author(self):
        """Автор может зайти на страницу редактирования."""
        self.client.login(email='author@example.com', password='password123')
        response = self.client.get(
            reverse('projects:edit', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 200)

    def test_project_edit_by_other_user(self):
        """Другой пользователь НЕ может редактировать проект (403 Forbidden)."""
        self.client.login(email='viewer@example.com', password='password123')
        response = self.client.get(
            reverse('projects:edit', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 403)

    def test_toggle_participate(self):
        """Тестируем AJAX-запрос на вступление в проект."""
        self.client.login(email='viewer@example.com', password='password123')

        # Отправляем POST запрос (как это делает JS)
        response = self.client.post(
            reverse('projects:toggle_participate',
                    kwargs={'pk': self.project.pk}),
            content_type='application/json'
        )

        # Проверяем ответ
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertTrue(response.json()['participant'])

        # Проверяем, что в базе появилась запись об участии
        self.assertTrue(ProjectMembership.objects.filter(
            user=self.viewer, project=self.project).exists())

    def test_toggle_favorite(self):
        """Тестируем AJAX-запрос на добавление в избранное."""
        self.client.login(email='viewer@example.com', password='password123')

        response = self.client.post(
            reverse('projects:toggle_favorite',
                    kwargs={'pk': self.project.pk}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['is_favorite'], True)

        # Проверяем, что проект добавился в favorites у пользователя
        self.assertIn(self.project, self.viewer.favorites.all())
