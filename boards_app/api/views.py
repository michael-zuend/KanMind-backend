"""API views for listing, creating, reading, updating and deleting boards."""

from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from boards_app.models import Board

from .permissions import IsBoardMemberOrOwner, IsBoardOwnerForDelete
from .serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
)


class BoardListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/boards/ - boards of the current user, create a board."""

    serializer_class = BoardListSerializer

    def get_queryset(self):
        """Return boards the user owns or is a member of."""
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        """Save the board with the requesting user as owner."""
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/boards/{id}/ - single board operations."""

    queryset = Board.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    permission_classes = [
        IsAuthenticated, IsBoardMemberOrOwner, IsBoardOwnerForDelete,
    ]

    def get_serializer_class(self):
        """Use the update serializer for PATCH, detail otherwise."""
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer