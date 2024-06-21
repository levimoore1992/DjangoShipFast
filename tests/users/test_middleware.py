from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from apps.users.middleware import TrackUserIPAndDeviceMiddleware
from apps.users.models import UserIP, UserDevice
from tests.factories.users import UserFactory


class TrackUserIPAndDeviceMiddlewareTest(TestCase):
    """
    TrackUserIpAdmin test cases
    """

    def setUp(self):
        """Setup tests"""
        super().setUp()
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.middleware = TrackUserIPAndDeviceMiddleware(
            get_response=lambda request: None
        )

    @patch("apps.users.middleware.get_client_ip", return_value=("123.123.123.123", True))
    @patch(
        "apps.users.middleware.get_device_identifier", return_value="unique-device-id"
    )
    def test_middleware_updates_userip_and_userdevice(
        self, mock_get_device_identifier, mock_get_client_ip
    ):
        """
        Test middleware upadtes userip and userdevice
        :param mock_get_device_identifier:
        :param mock_get_client_ip:
        :return:
        """
        # Simulate a request
        request = self.factory.get("/")
        request.user = self.user
        self.middleware(request)

        # Check that UserIP and UserDevice have been updated
        self.assertTrue(
            UserIP.objects.filter(user=self.user, ip_address="123.123.123.123").exists()
        )
        self.assertTrue(
            UserDevice.objects.filter(
                user=self.user, device_identifier="unique-device-id"
            ).exists()
        )

    def test_middleware_does_not_track_unauthenticated_users(self):
        """
        Test middleware doesnt track unauthenticated users
        :return:
        """
        # Simulate a request from an unauthenticated user
        request = self.factory.get("/")
        request.user = AnonymousUser()
        self.middleware(request)

        # Check that no UserIP or UserDevice records are created
        self.assertFalse(UserIP.objects.exists())
        self.assertFalse(UserDevice.objects.exists())
