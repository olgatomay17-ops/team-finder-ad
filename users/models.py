from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.id}/{filename}'


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True,
    )

    class Meta:
        abstract = True


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        unique=True,
        help_text='Необходимо для входа в систему',
    )
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    avatar = models.ImageField(
        "Аватар",
        upload_to=user_avatar_path,
        blank=True,
        help_text='Загрузите аватарку'
    )
    bio = models.TextField(
        'О себе',
        blank=True,
        max_length=1000,
        help_text='Кратко напишите о себе')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    github = models.URLField('GtHub', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['-date_joined']),
        ] # индексы для базы данных

    def _str_(self):
        return f'{self.last_name} {self.first_name}'.strip() or self.email   

    # @property
    # def full_name(self):
    #     return f'{self.last_name} {self.first_name}'.strip()


class Skill(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)

    class Meta:
        verbose_name='Навык'
        verbose_name_plural='Навыки'
        ordering = ['name']

    def _str_(self):
        return self.name


class UserSkill(BaseModel):  
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_skills',
        verbose_name='Пользователь',
    ) 
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='user_skills',
        verbose_name='Навык',
    )

    class Meta:
        verbose_name = 'Навык пользователя'
        verbose_name_plural = 'Навыки пользователей'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'skill'],
                name='unique_user_skill'
            ),
        ]

    def _srt_(self):
        return f'{self.user} - {self.skill}'    