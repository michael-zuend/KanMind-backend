"""API views for tasks and their comments."""

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from boards_app.models import Board
from tasks_app.models import Task

from .permissions import IsTaskBoardMember, IsTaskCreatorOrBoardOwnerForDelete
from .serializers import (
    CommentSerializer,
    TaskSerializer,
    TaskUpdateSerializer,
)

NOT_A_MEMBER = 'You must be a member of this board.'


def get_task_for_member(task_id, user):
    """Return the task (404 if missing) if the user may access its board."""
    task = get_object_or_404(Task, pk=task_id)
    if not task.board.has_access(user):
        raise PermissionDenied(NOT_A_MEMBER)
    return task


class TaskCreateView(generics.CreateAPIView):
    """POST /api/tasks/ - create a task on a board the user belongs to."""

    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        """Check board existence and membership before validating."""
        self.check_board_membership(request.data.get('board'))
        return super().create(request, *args, **kwargs)

    def check_board_membership(self, board_id):
        """Raise 404/403 for unknown boards or non-members."""
        if not str(board_id).isdigit():
            return
        board = get_object_or_404(Board, pk=int(board_id))
        if not board.has_access(self.request.user):
            raise PermissionDenied(NOT_A_MEMBER)

    def perform_create(self, serializer):
        """Store the requesting user as creator."""
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    """PATCH/DELETE /api/tasks/{id}/ - update or delete a task."""

    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer
    http_method_names = ['patch', 'delete', 'options']
    permission_classes = [
        IsAuthenticated, IsTaskBoardMember,
        IsTaskCreatorOrBoardOwnerForDelete,
    ]


class UserTaskListView(generics.ListAPIView):
    """Base list view returning tasks related to the current user."""

    serializer_class = TaskSerializer
    user_field = None

    def get_queryset(self):
        """Filter tasks by the configured user field."""
        return Task.objects.filter(**{self.user_field: self.request.user})


class AssignedTaskListView(UserTaskListView):
    """GET /api/tasks/assigned-to-me/ - tasks assigned to the user."""

    user_field = 'assignee'


class ReviewingTaskListView(UserTaskListView):
    """GET /api/tasks/reviewing/ - tasks the user has to review."""

    user_field = 'reviewer'


class CommentListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/tasks/{task_id}/comments/ - list or add comments."""

    serializer_class = CommentSerializer

    def get_task(self):
        """Return the task from the URL if the user may access it."""
        return get_task_for_member(self.kwargs['task_id'], self.request.user)

    def get_queryset(self):
        """Comments of the task, oldest first."""
        return self.get_task().comments.all()

    def perform_create(self, serializer):
        """Attach task and author to the new comment."""
        serializer.save(task=self.get_task(), author=self.request.user)


class CommentDeleteView(generics.DestroyAPIView):
    """DELETE /api/tasks/{task_id}/comments/{comment_id}/ - author only."""

    def get_object(self):
        """Return the comment if the requesting user is its author."""
        task = get_task_for_member(self.kwargs['task_id'], self.request.user)
        comment = get_object_or_404(
            task.comments, pk=self.kwargs['comment_id']
        )
        if comment.author_id != self.request.user.id:
            raise PermissionDenied('Only the author can delete a comment.')
        return comment
