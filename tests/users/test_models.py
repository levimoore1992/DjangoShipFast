from django.test import TestCase

from tests.factories.users import UserFactory, UserDeviceFactory, UserIPFactory
from apps.users.models import User, UserIP, UserDevice


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


class UserIPManagerTests(TestCase):
    """
    Test the UserIPManager
    """

    def setUp(self):
        """
        Create a user and two user IPs
        :return:
        """
        self.user = UserFactory(username="testuser", password="12345")
        self.ip_address = "192.168.1.1"
        UserIPFactory(user=self.user, ip_address=self.ip_address, is_blocked=True)
        UserIPFactory(user=self.user, ip_address="192.168.1.2", is_suspicious=True)

    def test_is_ip_blocked_or_suspicious(self):
        """
        Test the is_ip_blocked_or_suspicious method
        :return:
        """
        self.assertTrue(UserIP.objects.is_ip_blocked_or_suspicious(self.ip_address))
        self.assertTrue(UserIP.objects.is_ip_blocked_or_suspicious("192.168.1.2"))
        self.assertFalse(UserIP.objects.is_ip_blocked_or_suspicious("10.0.0.1"))

    def test_get_ip_history_for_user(self):
        """
        Test the get_ip_history_for_user method
        :return:
        """
        ip_history = UserIP.objects.get_ip_history_for_user(self.user.id)
        self.assertEqual(ip_history.count(), 2)
        self.assertIn(self.ip_address, ip_history.values_list("ip_address", flat=True))


class UserDeviceManagerTests(TestCase):
    """
    Test the UserDeviceManager
    """

    def setUp(self):
        """
        Create a user and a user device
        :return:
        """
        self.user = UserFactory(username="testdeviceuser", password="12345")
        self.device_identifier = "device123"
        UserDeviceFactory(
            user=self.user, device_identifier=self.device_identifier, is_blocked=True
        )

    def test_is_device_blocked(self):
        """
        Test the is_device_blocked method
        :return:
        """
        self.assertTrue(UserDevice.objects.is_device_blocked(self.device_identifier))
        self.assertFalse(UserDevice.objects.is_device_blocked("device999"))

    def test_get_device_history_for_user(self):
        """
        Test the get_device_history_for_user method
        :return:
        """
        device_history = UserDevice.objects.get_device_history_for_user(self.user.id)
        self.assertEqual(device_history.count(), 1)
        self.assertIn(
            self.device_identifier,
            device_history.values_list("device_identifier", flat=True),
        )
