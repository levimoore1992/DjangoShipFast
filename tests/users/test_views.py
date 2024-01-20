from django.urls import reverse
from tests.base import BaseTestCase
from tests.factories.users import UserFactory
from users.forms import UserCreationForm
from users.models import User


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
