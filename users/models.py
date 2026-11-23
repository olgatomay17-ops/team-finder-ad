from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .utils import generate_avatar

USER_NAME_MAX_LENGTH = 124
USER_SURNAME_MAX_LENGTH = 124

USER_BIO_MAX_LENGTH = 256
USER_PHONE_MAX_LENGTH = 12


def user_avatar_path(instance, filename):
    return f"avatars/{filename}"


class UserManager(BaseUserManager):
    # use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(
        "Email",
        unique=True,
        help_text="Необходимо для входа в систему",
    )
    name = models.CharField(
        "Имя",
        max_length=USER_NAME_MAX_LENGTH,
    )
    surname = models.CharField(
        "Фамилия",
        max_length=USER_SURNAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        "Аватар",
        upload_to=user_avatar_path,
        blank=True,
    )
    about = models.TextField(
        "О себе",
        blank=True,
        max_length=USER_BIO_MAX_LENGTH,
    )
    phone = models.CharField(
        "Телефон",
        max_length=USER_PHONE_MAX_LENGTH,
    )
    github_url = models.URLField("GitHub", blank=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="favorited_by",
        blank=True,
        verbose_name="Избранные проекты",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email

    def save(self, *args, **kwargs):
        """Генерируется аватар при первом сохр"""
        if not self.pk and not self.avatar:
            self.avatar = generate_avatar(self.name)
        super().save(*args, **kwargs)
