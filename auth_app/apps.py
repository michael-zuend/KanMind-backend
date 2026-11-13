"""App configuration for auth_app."""

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Configuration of the auth app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
