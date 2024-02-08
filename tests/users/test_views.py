from unittest.mock import patch

from django.contrib.messages import get_messages
from django.urls import reverse
from tests.base import BaseTestCase
from tests.factories.users import UserFactory, UserIPFactory
from apps.users.forms import UserCreationForm
from apps.users.models import User


class BaseAuthenticationTest(BaseTestCase):
    """Base test case for authentication-related views."""

    def setUp(self) -> None:
        """Setup common attributes for authentication tests."""
        super().setUp()
        self.user_password = (
            "default-password"  # Adjust if a different password is used.
        )

    def login(self, user=None):
        """Login a user using the test client."""
        user = user or self.regular_user
        self.client.login(username=user.username, password=self.user_password)


class LoginViewTest(BaseAuthenticationTest):
    """Test cases for the LoginView."""

    def setUp(self) -> None:
        """Setup common attributes for login tests."""
        super().setUp()
        self.user = UserFactory(username="testuser")
        self.user.set_password("12345")
        self.user.save()

    def test_login_form_invalid(self) -> None:
        """Test if an error is added when form is invalid."""
        response = self.client.post(reverse("login"), {"username": "", "password": ""})
        self.assertIn("Invalid username or password.", str(response.content))

    def test_get_success_url(self):
        """
        Test the get_success_url method to ensure it redirects to the home page after successful login.
        """
        # Login with valid credentials
        self.client.login(username="testuser", password="12345")

        # Post to the login URL
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "12345"}, follow=True
        )

        # Check if it redirects to the home page
        self.assertRedirects(response, reverse("home"))


class RegisterViewTest(BaseAuthenticationTest):
    """Test cases for the RegisterView."""

    def test_register_post_valid(self) -> None:
        """Test registration with valid data."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
            "g-recaptcha-response": "test",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_get_context_data(self):
        """Test that the register view includes the UserCreationForm in its context."""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], UserCreationForm)

    def test_register_post_invalid(self):
        """Test registration with invalid data."""
        data = {
            "username": "newuser",
            "password1": "testpassword123",  # intentionally missing password2
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(
            response.status_code, 200
        )  # Should render the form again with errors
        self.assertFalse(User.objects.filter(username="newuser").exists())
        self.assertIn("form", response.context)  # Check that form is in the context
        self.assertFalse(response.context["form"].is_valid())  # Form should be invalid

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    @patch(
        "apps.users.views.get_device_identifier", return_value="test-device-identifier"
    )
    @patch("apps.users.views.get_client_ip", return_value=("192.168.1.100", True))
    def test_user_registration_with_blocked_ip(
        self, mock_get_client_ip, mock_get_device_identifier, mock_validate
    ):
        """
        Test that a user cannot register if their IP is blocked.
        :param mock_get_client_ip:
        :param mock_get_device_identifier:
        :param mock_validate:
        :return:
        """
        mock_validate.return_value = None
        UserIPFactory.create(ip_address="192.168.1.100", is_blocked=True)

        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
            "activation_code": "",
            "g-recaptcha-response": "PASSED",
        }

        response = self.client.post(reverse("register"), user_data)
        new_user = User.objects.filter(username="newuser").first()

        self.assertIsNotNone(new_user, "The new user should have been created.")
        self.assertFalse(new_user.is_active, "The new user should not be active.")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("problem with your account" in str(message) for message in messages)
        )


class LogoutViewTest(BaseAuthenticationTest):
    """Test cases for the LogoutView."""

    def test_logout(self) -> None:
        """Test if user is redirected after logout."""
        self.login()
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)


class PasswordResetConfirmViewTest(BaseAuthenticationTest):
    """Test cases for the PasswordResetConfirmView."""

    def test_context_data(self) -> None:
        """Test if uidb64 and token are in context."""
        url = reverse(
            "password_reset_confirm", kwargs={"uidb64": "testuid", "token": "testtoken"}
        )
        response = self.client.get(url)

        self.assertIn("uidb64", response.context_data)
        self.assertIn("token", response.context_data)
        self.assertEqual(response.context_data["uidb64"], "testuid")
        self.assertEqual(response.context_data["token"], "testtoken")
