import os
import io
import random
import uuid
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
def user_avatar_path(instance, filename):
    return f'avatars/{filename}'


class UserManager(BaseUserManager):
    # use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(
        'Email',
        unique=True,
        help_text='Необходимо для входа в систему',
    )
    name = models.CharField('Имя', max_length=124)
    surname = models.CharField('Фамилия', max_length=124)
    avatar = models.ImageField(
        "Аватар",
        upload_to=user_avatar_path,
        blank=True,
    )
    about = models.TextField('О себе', blank=True, max_length=256)
    phone = models.CharField('Телефон', max_length=12)
    github_url = models.URLField('GitHub', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['name', 'surname', 'phone']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
        # indexes = [
        #     models.Index(fields=['-date_joined']),
        # ] # индексы для базы данных

    def __str__(self):
        return f'{self.surname} {self.name}'.strip() or self.email

    def save(self,*args, **kwargs):
        """Генерируется аватар при первом сохр"""
        if not self.pk and not self.avatar:
            self.avatar = self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        size = 200
        color = tuple(random.randint(60, 140) for _ in range(3))
        image = Image.new('RGB', (size,size), color)
        draw = ImageDraw.Draw(image)
        letter = (self.name)[0].upper()

        fontPath = finders.find(
            'fonts/Neue_Haas_Grotesk_Display_Pro_75_Bold.otf'
        )
        font = (
            ImageFont.truetype(fontPath, 110)
            if fontPath and os.path.exists(fontPath)
            else ImageFont.load_default()
        )

        bbox = draw.textbbox((0, 0), letter, font=font)
        x = (size - (bbox[2] - bbox[0])) / 2 - bbox[0]
        y = (size - (bbox[3] - bbox[1])) / 2 - bbox[1]
        draw.text((x, y), letter, fill=(255, 255, 255), font=font)

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return ContentFile(
            buffer.getvalue(),
            name=f'avatar_{uuid.uuid4()}.png',
        )


class Skill(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)

    class Meta:
        verbose_name='Навык'
        verbose_name_plural='Навыки'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserSkill(models.Model):  
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
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

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

    def __str__(self):
        return f'{self.user} - {self.skill}'