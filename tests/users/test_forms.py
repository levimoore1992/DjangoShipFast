from users.forms import UserCreationForm

from tests.base import BaseTestCase


class UserCreationFormTest(BaseTestCase):
    """Test cases for the UserCreationForm."""

    def setUp(self) -> None:
        """Setup the initial data for the tests."""
        super().setUp()  # Ensure BaseTestCase's setup is also executed
        self.valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
            "g-recaptcha-response": "test",
        }
        self.mismatch_password_data = self.valid_data.copy()
        self.mismatch_password_data["password2"] = "wrongpassword"

    def test_valid_form(self) -> None:
        """Test that the form is valid with the correct data."""
        form = UserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self) -> None:
        """Test that the form is invalid if passwords don't match."""
        form = UserCreationForm(data=self.mismatch_password_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["Passwords don't match"])

    def test_save_user(self) -> None:
        """Test the save method to ensure it saves a user with a hashed password."""
        form = UserCreationForm(data=self.valid_data)
        if form.is_valid():
            user = form.save()
            self.assertTrue(user.check_password(self.valid_data["password1"]))
