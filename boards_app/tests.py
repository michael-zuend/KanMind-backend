"""Tests for the board endpoints."""

from boards_app.models import Board
from core.test_utils import KanMindAPITestCase

LIST_URL = '/api/boards/'


def detail_url(board_id):
    """URL of a single board."""
    return f'/api/boards/{board_id}/'


class BoardListCreateTests(KanMindAPITestCase):
    """GET/POST /api/boards/."""

    def test_list_contains_counts(self):
        """List contains counts."""
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, 200)
        board = response.data[0]
        self.assertEqual(board['member_count'], 2)
        self.assertEqual(board['ticket_count'], 1)
        self.assertEqual(board['tasks_to_do_count'], 1)
        self.assertEqual(board['tasks_high_prio_count'], 1)
        self.assertEqual(board['owner_id'], self.owner.id)

    def test_list_hides_foreign_boards(self):
        """List hides foreign boards."""
        response = self.client_for(self.outsider).get(LIST_URL)
        self.assertEqual(response.data, [])

    def test_create_board_adds_owner(self):
        """Create board adds owner."""
        data = {'title': 'New', 'members': [self.member.id]}
        response = self.client.post(LIST_URL, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['member_count'], 2)

    def test_create_board_invalid(self):
        """Create board invalid."""
        response = self.client.post(LIST_URL, {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated(self):
        """Unauthenticated."""
        self.client.credentials()
        self.assertEqual(self.client.get(LIST_URL).status_code, 401)


class BoardDetailTests(KanMindAPITestCase):
    """GET/PATCH/DELETE /api/boards/{id}/."""

    def test_retrieve_board(self):
        """Retrieve board."""
        response = self.client_for(self.member).get(detail_url(self.board.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']), 2)
        self.assertEqual(response.data['tasks'][0]['comments_count'], 0)

    def test_retrieve_without_trailing_slash(self):
        """Retrieve without trailing slash."""
        response = self.client.get(f'/api/boards/{self.board.id}')
        self.assertEqual(response.status_code, 200)

    def test_retrieve_forbidden_and_missing(self):
        """Retrieve forbidden and missing."""
        outsider = self.client_for(self.outsider)
        response = outsider.get(detail_url(self.board.id))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.get(detail_url(999)).status_code, 404)

    def test_patch_title_and_members(self):
        """Patch title and members."""
        data = {'title': 'Renamed', 'members': [self.outsider.id]}
        response = self.client.patch(
            detail_url(self.board.id), data, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['owner_data']['id'], self.owner.id)
        self.assertEqual(len(response.data['members_data']), 2)

    def test_patch_title_only_keeps_members(self):
        """Patch title only keeps members."""
        response = self.client.patch(
            detail_url(self.board.id), {'title': 'Only'}, format='json'
        )
        self.assertEqual(len(response.data['members_data']), 2)

    def test_delete_only_owner(self):
        """Delete only owner."""
        member = self.client_for(self.member)
        self.assertEqual(
            member.delete(detail_url(self.board.id)).status_code, 403
        )
        response = self.client.delete(detail_url(self.board.id))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Board.objects.exists())

    def test_str(self):
        """Str."""
        self.assertEqual(str(self.board), 'Board')
