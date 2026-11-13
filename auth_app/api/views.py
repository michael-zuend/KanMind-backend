"""API views for registration, login and the email check."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserShortSerializer,
)

User = get_user_model()


def is_valid_email(value):
    """Return True if the given string is a syntactically valid email."""
    try:
        validate_email(value)
    except ValidationError:
        return False
    return True


def build_auth_response(user):
    """Return the token payload the frontend stores after login."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'fullname': user.fullname,
        'email': user.email,
        'user_id': user.id,
    }


class RegistrationView(APIView):
    """POST /api/registration/ - create an account and return a token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            build_auth_response(user), status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """POST /api/login/ - authenticate with email and password."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Log the user in and return a token."""
        serializer = LoginSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(build_auth_response(user), status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """GET /api/email-check/?email=... - look up a user by email."""

    def get(self, request):
        """Return the user owning the email, 400 if invalid, 404 if none."""
        email = request.query_params.get('email', '').strip()
        if not is_valid_email(email):
            error = {'email': 'A valid email address is required.'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            error = {'detail': 'Email not found.'}
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        return Response(UserShortSerializer(user).data)
