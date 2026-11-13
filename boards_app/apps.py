"""App configuration for boards_app."""

from django.apps import AppConfig


class BoardsAppConfig(AppConfig):
    """Configuration of the boards app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boards_app'
