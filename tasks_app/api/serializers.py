"""Serializers for tasks and comments."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from auth_app.api.serializers import UserShortSerializer
from tasks_app.models import Comment, Task

User = get_user_model()

TASK_FIELDS = [
    'id', 'board', 'title', 'description', 'status', 'priority',
    'assignee', 'reviewer', 'assignee_id', 'reviewer_id', 'due_date',
    'comments_count',
]


def user_id_field(source):
    """Writable user id field mapped to the given model field."""
    return serializers.PrimaryKeyRelatedField(
        source=source, queryset=User.objects.all(), write_only=True,
        allow_null=True, required=False,
    )


class TaskSerializer(serializers.ModelSerializer):
    """Task with nested assignee/reviewer and the number of comments."""

    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    assignee_id = user_id_field('assignee')
    reviewer_id = user_id_field('reviewer')
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = TASK_FIELDS

    def get_comments_count(self, obj):
        """Number of comments on the task."""
        return obj.comments.count()

    def validate(self, attrs):
        """Assignee and reviewer must be members of the task's board."""
        board = attrs.get('board') or self.instance.board
        for field in ('assignee', 'reviewer'):
            user = attrs.get(field)
            if user is not None and not board.has_access(user):
                raise serializers.ValidationError(
                    {f'{field}_id': 'User is not a member of this board.'}
                )
        return attrs


class BoardTaskSerializer(TaskSerializer):
    """Task representation nested in the board detail view."""

    class Meta(TaskSerializer.Meta):
        fields = [f for f in TASK_FIELDS if f != 'board']


class TaskUpdateSerializer(TaskSerializer):
    """Task update; the board of a task cannot be changed."""

    class Meta(TaskSerializer.Meta):
        fields = [
            f for f in TASK_FIELDS if f not in ('board', 'comments_count')
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Comment with the author's full name."""

    author = serializers.CharField(source='author.fullname', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
