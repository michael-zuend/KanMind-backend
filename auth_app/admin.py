"""Admin registration for the custom user model."""

from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Simple admin list view for users."""

    list_display = ('id', 'email', 'fullname', 'is_staff')
    search_fields = ('email', 'fullname')
