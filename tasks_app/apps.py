"""App configuration for tasks_app."""

from django.apps import AppConfig


class TasksAppConfig(AppConfig):
    """Configuration of the tasks app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks_app'
