"""Board model: a kanban board owned by one user and shared with members."""

from django.conf import settings
from django.db import models


class Board(models.Model):
    """A kanban board that groups tasks and its members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_boards',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='boards',
        blank=True,
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        """Return the board title."""
        return self.title

    def has_access(self, user):
        """Return True if the user is the owner or a member of the board."""
        return (
            self.owner_id == user.id
            or self.members.filter(pk=user.pk).exists()
        )