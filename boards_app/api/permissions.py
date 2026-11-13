"""Object-level permissions for boards."""

from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """Allow access to board members and the board owner."""

    message = 'You must be a member or the owner of this board.'

    def has_object_permission(self, request, view, obj):
        """Check membership on the board instance."""
        return obj.has_access(request.user)


class IsBoardOwnerForDelete(BasePermission):
    """Only the owner of a board may delete it."""

    message = 'Only the board owner can delete this board.'

    def has_object_permission(self, request, view, obj):
        """Allow DELETE only for the owner; other methods pass through."""
        if request.method != 'DELETE':
            return True
        return obj.owner_id == request.user.id