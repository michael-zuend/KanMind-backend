"""Admin registration for boards."""

from django.contrib import admin

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin list view for boards."""

    list_display = ('id', 'title', 'owner')
    search_fields = ('title',)
