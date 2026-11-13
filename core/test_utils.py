"""Shared helpers for the API test suites."""

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from boards_app.models import Board
from tasks_app.models import Task

User = get_user_model()


def create_user(email, fullname='Test User', password='secret123'):
    """Create a user with a default password."""
    return User.objects.create_user(
        email=email, fullname=fullname, password=password
    )


class KanMindAPITestCase(APITestCase):
    """Base test case with an owner, a member, an outsider and a board."""

    def setUp(self):
        """Create users, a shared board and one task."""
        self.owner = create_user('owner@test.de', 'Owner Person')
        self.member = create_user('member@test.de', 'Member Person')
        self.outsider = create_user('outsider@test.de', 'Out Sider')
        self.board = Board.objects.create(title='Board', owner=self.owner)
        self.board.members.set([self.owner, self.member])
        self.task = Task.objects.create(
            board=self.board, title='Task', created_by=self.member,
            assignee=self.member, reviewer=self.owner, priority='high',
        )
        self.client = self.client_for(self.owner)

    def client_for(self, user):
        """Return an API client authenticated with the user's token."""
        client = APIClient()
        token, _ = Token.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return client
