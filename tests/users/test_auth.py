from unittest.mock import patch
from django.test import TestCase, Client
from apps.users.auth import DjangoAdminAuthBackend
from apps.users.models import User


class DjangoAdminAuthBackendTests(TestCase):
    """
    Unit tests for the DjangoAdminAuthBackend authentication class.
    """

    def setUp(self):
        """
        Set up the test case with a client, authentication backend, and a request.
        """
        super().setUp()
        self.client = Client()
        self.backend = DjangoAdminAuthBackend()
        self.request = self.client.get("/")

    @patch("apps.users.models.User.objects.get")
    def test_authenticate_success(self, mock_get):
        """
        Test successful authentication when the user exists and has access.
        """
        mock_user = User(email="staff@example.com", is_staff=True, is_active=True)
        mock_get.return_value = mock_user

        user = self.backend.authenticate(
            self.request.wsgi_request, sso_email="staff@example.com"
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "staff@example.com")
        mock_get.assert_called_with(
            is_staff=True, is_active=True, email="staff@example.com"
        )

    @patch("apps.users.models.User.objects.get")
    def test_authenticate_no_sso_email(self, mock_get):
        """
        Test authentication when no SSO email is provided.
        """
        user = self.backend.authenticate(self.request.wsgi_request)

        self.assertIsNone(user)
        mock_get.assert_not_called()

    @patch("apps.users.models.User.objects.get")
    @patch("apps.users.auth.messages")
    def test_authenticate_user_does_not_exist(self, mock_messages, mock_get):
        """
        Test authentication when the user does not exist.
        """
        mock_get.side_effect = User.DoesNotExist

        user = self.backend.authenticate(
            self.request.wsgi_request, sso_email="nonexistent@example.com"
        )

        self.assertIsNone(user)
        mock_get.assert_called_with(
            is_staff=True, is_active=True, email="nonexistent@example.com"
        )
        mock_messages.error.assert_called_once_with(
            self.request.wsgi_request,
            "Your email address does not have access to this site. "
            "Please contact an administrator to fix this issue.",
        )

    @patch("apps.users.auth.logger")
    @patch("apps.users.models.User.objects.get")
    @patch("apps.users.auth.messages")
    def test_authenticate_user_does_not_exist_logs_error(
        self, mock_messages, mock_get, mock_logger
    ):
        """
        Test that an error is logged when the user does not exist.
        """
        mock_get.side_effect = User.DoesNotExist

        user = self.backend.authenticate(
            self.request.wsgi_request, sso_email="nonexistent@example.com"
        )

        self.assertIsNone(user)
        mock_get.assert_called_with(
            is_staff=True, is_active=True, email="nonexistent@example.com"
        )
        mock_logger.error.assert_called_once_with(
            "A user that did not have access to the site attempted to access it. %s",
            "nonexistent@example.com",
        )
        mock_messages.error.assert_called_once_with(
            self.request.wsgi_request,
            "Your email address does not have access to this site. "
            "Please contact an administrator to fix this issue.",
        )
