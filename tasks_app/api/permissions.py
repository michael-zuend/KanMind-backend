"""Object-level permissions for tasks and comments."""

from rest_framework.permissions import BasePermission


class IsTaskBoardMember(BasePermission):
    """Allow access if the user is a member or owner of the task's board."""

    message = 'You must be a member of the board of this task.'

    def has_object_permission(self, request, view, obj):
        """Check membership on the task's board."""
        return obj.board.has_access(request.user)


class IsTaskCreatorOrBoardOwnerForDelete(BasePermission):
    """Only the task creator or the board owner may delete a task."""

    message = 'Only the task creator or the board owner can delete it.'

    def has_object_permission(self, request, view, obj):
        """Allow DELETE only for creator or board owner."""
        if request.method != 'DELETE':
            return True
        user_id = request.user.id
        return user_id in (obj.created_by_id, obj.board.owner_id)
