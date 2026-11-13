"""Serializers for the board endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from auth_app.api.serializers import UserShortSerializer
from boards_app.models import Board
from tasks_app.api.serializers import BoardTaskSerializer
from tasks_app.models import Task

User = get_user_model()


class BoardListSerializer(serializers.ModelSerializer):
    """Board overview with counters; also used to create a board."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True,
        required=False,
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'members', 'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id',
        ]

    def get_member_count(self, obj):
        """Number of board members (the owner is always a member)."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Total number of tasks on the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Number of tasks in the 'to-do' column."""
        return obj.tasks.filter(status=Task.Status.TO_DO).count()

    def get_tasks_high_prio_count(self, obj):
        """Number of tasks with high priority."""
        return obj.tasks.filter(priority=Task.Priority.HIGH).count()

    def create(self, validated_data):
        """Create the board and add the owner to its members."""
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set({*members, board.owner})
        return board


class BoardDetailSerializer(serializers.ModelSerializer):
    """Full board including its members and tasks."""

    owner_id = serializers.IntegerField(read_only=True)
    members = UserShortSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Update title and/or members; returns owner and member details."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True,
        required=False,
    )
    owner_data = UserShortSerializer(source='owner', read_only=True)
    members_data = UserShortSerializer(
        source='members', many=True, read_only=True
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']

    def update(self, instance, validated_data):
        """Apply changes; the owner always stays a member."""
        members = validated_data.pop('members', None)
        instance = super().update(instance, validated_data)
        if members is not None:
            instance.members.set({*members, instance.owner})
        return instance