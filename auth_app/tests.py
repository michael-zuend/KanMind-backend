"""Tests for registration, login and email check endpoints."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from core.test_utils import KanMindAPITestCase, create_user

User = get_user_model()


class RegistrationTests(APITestCase):
    """POST /api/registration/."""

    url = '/api/registration/'
    payload = {
        'fullname': 'Max Mustermann', 'email': 'max@test.de',
        'password': 'secret123', 'repeated_password': 'secret123',
    }

    def test_register_success(self):
        """Register success."""
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            set(response.data), {'token', 'fullname', 'email', 'user_id'}
        )

    def test_register_password_mismatch(self):
        """Register password mismatch."""
        data = {**self.payload, 'repeated_password': 'other'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_email(self):
        """Register duplicate email."""
        create_user('max@test.de')
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, 400)


class LoginTests(APITestCase):
    """POST /api/login/."""

    url = '/api/login/'

    def setUp(self):
        """Create test fixtures."""
        self.user = create_user('login@test.de', 'Log In')

    def test_login_success(self):
        """Login success."""
        data = {'email': 'login@test.de', 'password': 'secret123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_id'], self.user.id)

    def test_login_wrong_password(self):
        """Login wrong password."""
        data = {'email': 'login@test.de', 'password': 'wrong'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)


class EmailCheckTests(KanMindAPITestCase):
    """GET /api/email-check/."""

    url = '/api/email-check/'

    def test_existing_email(self):
        """Existing email."""
        response = self.client.get(self.url, {'email': 'member@test.de'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.member.id)

    def test_unknown_email(self):
        """Unknown email."""
        response = self.client.get(self.url, {'email': 'nobody@test.de'})
        self.assertEqual(response.status_code, 404)

    def test_invalid_email(self):
        """Invalid email."""
        response = self.client.get(self.url, {'email': 'no-mail'})
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated(self):
        """Unauthenticated."""
        self.client.credentials()
        response = self.client.get(self.url, {'email': 'member@test.de'})
        self.assertEqual(response.status_code, 401)


class UserModelTests(TestCase):
    """User manager and model helpers."""

    def test_create_user_requires_email(self):
        """Create user requires email."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='x')

    def test_create_superuser(self):
        """Create superuser."""
        admin = User.objects.create_superuser(
            email='admin@test.de', password='x', fullname='Ad Min'
        )
        self.assertTrue(admin.is_superuser and admin.is_staff)
        self.assertEqual(str(admin), 'Ad Min')
