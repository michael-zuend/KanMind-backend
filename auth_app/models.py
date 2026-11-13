"""Custom user model that logs in with email instead of a username."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Manager creating users identified by their email address."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email."""
        if not email:
            raise ValueError('The email address must be set.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with admin rights."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """KanMind user with a unique email and a single full-name field."""

    username = None
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    objects = UserManager()

    def __str__(self):
        """Return the full name for admin and shell output."""
        return self.fullname
