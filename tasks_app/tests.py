"""Tests for task and comment endpoints."""

from core.test_utils import KanMindAPITestCase
from tasks_app.models import Comment, Task

TASKS_URL = '/api/tasks/'


def task_url(task_id):
    """URL of a single task."""
    return f'/api/tasks/{task_id}/'


def comments_url(task_id):
    """URL of the comment list of a task."""
    return f'/api/tasks/{task_id}/comments/'


class TaskCreateTests(KanMindAPITestCase):
    """POST /api/tasks/."""

    def payload(self, **overrides):
        """Valid task payload, optionally overridden."""
        data = {
            'board': self.board.id, 'title': 'New task',
            'description': 'Desc', 'status': 'review', 'priority': 'low',
            'assignee_id': self.member.id, 'reviewer_id': None,
            'due_date': '2026-12-01',
        }
        return {**data, **overrides}

    def test_create_task(self):
        """Create task."""
        response = self.client.post(TASKS_URL, self.payload(), format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['assignee']['id'], self.member.id)
        self.assertIsNone(response.data['reviewer'])
        self.assertEqual(response.data['comments_count'], 0)

    def test_create_assignee_not_member(self):
        """Create assignee not member."""
        data = self.payload(assignee_id=self.outsider.id)
        response = self.client.post(TASKS_URL, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_not_member(self):
        """Create not member."""
        client = self.client_for(self.outsider)
        response = client.post(TASKS_URL, self.payload(), format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_board_missing_or_invalid(self):
        """Create board missing or invalid."""
        missing = self.client.post(
            TASKS_URL, self.payload(board=999), format='json'
        )
        self.assertEqual(missing.status_code, 404)
        invalid = self.client.post(
            TASKS_URL, self.payload(board=None), format='json'
        )
        self.assertEqual(invalid.status_code, 400)


class TaskDetailTests(KanMindAPITestCase):
    """PATCH/DELETE /api/tasks/{id}/."""

    def test_patch_status(self):
        """Patch status."""
        response = self.client_for(self.member).patch(
            task_url(self.task.id), {'status': 'done'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'done')
        self.assertNotIn('board', response.data)

    def test_patch_reviewer_not_member(self):
        """Patch reviewer not member."""
        response = self.client.patch(
            task_url(self.task.id), {'reviewer_id': self.outsider.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_forbidden_and_missing(self):
        """Patch forbidden and missing."""
        outsider = self.client_for(self.outsider)
        response = outsider.patch(task_url(self.task.id), {}, format='json')
        self.assertEqual(response.status_code, 403)
        missing = self.client.patch(task_url(999), {}, format='json')
        self.assertEqual(missing.status_code, 404)

    def test_delete_by_creator(self):
        """Delete by creator."""
        response = self.client_for(self.member).delete(task_url(self.task.id))
        self.assertEqual(response.status_code, 204)

    def test_delete_by_board_owner(self):
        """Delete by board owner."""
        response = self.client.delete(task_url(self.task.id))
        self.assertEqual(response.status_code, 204)

    def test_delete_forbidden(self):
        """Delete forbidden."""
        self.task.created_by = self.owner
        self.task.save()
        response = self.client_for(self.member).delete(task_url(self.task.id))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(self.task), 'Task')


class TaskListTests(KanMindAPITestCase):
    """GET /api/tasks/assigned-to-me/ and /api/tasks/reviewing/."""

    def test_assigned_to_me(self):
        """Assigned to me."""
        response = self.client_for(self.member).get(
            TASKS_URL + 'assigned-to-me/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['board'], self.board.id)

    def test_reviewing(self):
        """Reviewing."""
        response = self.client.get(TASKS_URL + 'reviewing/')
        self.assertEqual(len(response.data), 1)
        member = self.client_for(self.member)
        self.assertEqual(member.get(TASKS_URL + 'reviewing/').data, [])


class CommentTests(KanMindAPITestCase):
    """Comment list, create and delete."""

    def setUp(self):
        """Create test fixtures."""
        super().setUp()
        self.comment = Comment.objects.create(
            task=self.task, author=self.member, content='Hello'
        )

    def test_list_comments(self):
        """List comments."""
        response = self.client.get(comments_url(self.task.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['author'], 'Member Person')
        self.assertEqual(str(self.comment), 'Hello')

    def test_create_comment(self):
        """Create comment."""
        response = self.client.post(
            comments_url(self.task.id), {'content': 'Hi'}, format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], 'Owner Person')

    def test_comments_forbidden_and_missing(self):
        """Comments forbidden and missing."""
        outsider = self.client_for(self.outsider)
        response = outsider.get(comments_url(self.task.id))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.get(comments_url(999)).status_code, 404)

    def test_delete_comment_only_author(self):
        """Delete comment only author."""
        url = f'{comments_url(self.task.id)}{self.comment.id}/'
        self.assertEqual(self.client.delete(url).status_code, 403)
        member = self.client_for(self.member)
        self.assertEqual(member.delete(url).status_code, 204)
        self.assertEqual(member.delete(url).status_code, 404)

    def test_task_cascade(self):
        """Task cascade."""
        self.task.delete()
        self.assertFalse(Task.objects.exists() or Comment.objects.exists())
