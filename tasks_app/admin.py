"""Admin registration for tasks and comments."""

from django.contrib import admin

from .models import Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin list view for tasks."""

    list_display = ('id', 'title', 'board', 'status', 'priority')
    list_filter = ('status', 'priority')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin list view for comments."""

    list_display = ('id', 'task', 'author', 'created_at')