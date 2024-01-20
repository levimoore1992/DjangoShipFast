from django.test import TestCase

from tests.factories.users import UserFactory
from users.models import User


class UserTest(TestCase):
    """
    Test the User model.
    """

    def test_user_creation(self):
        """
        Test the creation of the User model.
        """
        user = UserFactory(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")

    def test_user_string_representation(self):
        """
        Test the string representation of the User model.
        """
        user = UserFactory(email="test@example.com")
        self.assertEqual(str(user), "test@example.com")

    def test_user_full_name_property(self):
        """
        Test the full_name property of the User model.
        """
        user = UserFactory(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )
        self.assertEqual(user.full_name, "Test User")
