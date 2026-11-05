from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Project(models.Model):

    STATUS_CHOICES = (
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    )

    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    github_url = models.URLField('Ссылка на GitHub', blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default='open'
    )
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    participants = models.ManyToManyField(
        User,
        through='ProjectMembership',
        related_name='participating_projects',
        verbose_name='Участники'
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.name)


class ProjectMembership(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Участник'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='membership',
        verbose_name='Проект'
    )
    joined_at = models.DateTimeField('Дата присоединения', auto_now_add=True)

    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проекта'
        ordering = ['-joined_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'project'],
                name='unique_user_project_membership'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.project}'
