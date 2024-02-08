import hashlib
from unittest.mock import patch

from django.test import TestCase, RequestFactory

from apps.users.utils import (
    block_user_and_devices,
    mark_ip_as_suspicious,
    block_ip,
    get_device_identifier,
)
from apps.users.models import UserDevice, UserIP, User


class UtilsTest(TestCase):
    """
    Test the utility functions
    """

    def setUp(self):
        """
        Create a user, a user device, and a user IP
        :return:
        """
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="12345"
        )
        self.user_device = UserDevice.objects.create(
            user=self.user, device_identifier="device123", is_blocked=False
        )
        self.user_ip = UserIP.objects.create(
            user=self.user, ip_address="192.168.1.1", is_blocked=False
        )

    @patch("apps.users.utils.send_email_task.delay")
    def test_block_user_and_devices(self, mock_send_email):
        """
        Test that block_user_and_devices sets the user to inactive,
         blocks the user's device, marks the user's IP as suspicious, and sends an email
        :param mock_send_email:
        :return:
        """
        block_user_and_devices(self.user.id)

        self.user.refresh_from_db()
        self.user_device.refresh_from_db()
        self.user_ip.refresh_from_db()

        self.assertFalse(self.user.is_active)
        self.assertTrue(self.user_device.is_blocked)
        self.assertTrue(self.user_ip.is_suspicious)
        mock_send_email.assert_called_once()

    def test_mark_ip_as_suspicious(self):
        """
        Test that mark_ip_as_suspicious sets the is_suspicious attribute to True
        :return:
        """
        mark_ip_as_suspicious("192.168.1.1")
        self.user_ip.refresh_from_db()
        self.assertTrue(self.user_ip.is_suspicious)

    def test_block_ip(self):
        """
        Test that block_ip sets the is_blocked attribute to True
        :return:
        """
        block_ip("192.168.1.1")
        self.user_ip.refresh_from_db()
        self.assertTrue(self.user_ip.is_blocked)

    def test_get_device_identifier(self):
        """
        Test that get_device_identifier returns the expected identifier
        :return:
        """
        request_factory = RequestFactory()
        request = request_factory.get(
            "/", HTTP_USER_AGENT="Mozilla/5.0", HTTP_ACCEPT_LANGUAGE="en-US"
        )

        device_identifier = get_device_identifier(request)
        expected_identifier = hashlib.sha256("Mozilla/5.0en-US".encode()).hexdigest()

        self.assertEqual(device_identifier, expected_identifier)
