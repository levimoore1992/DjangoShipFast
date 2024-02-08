from unittest.mock import patch
from django.test import TestCase, RequestFactory

from tests.factories.users import UserFactory
from users.middleware import TrackUserIPAndDeviceMiddleware
from users.models import UserIP, UserDevice


class TrackUserIPAndDeviceMiddlewareTest(TestCase):
    """
    Test the TrackUserIPAndDeviceMiddleware
    """

    def setUp(self):
        """
        Create a user and a request factory
        :return:
        """
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.middleware = TrackUserIPAndDeviceMiddleware(
            get_response=lambda request: None
        )

    @patch("users.middleware.get_client_ip", return_value=("123.123.123.123", True))
    @patch("users.middleware.get_device_identifier", return_value="unique-device-id")
    @patch("users.middleware.requests.get")
    def test_middleware_updates_userip_and_userdevice(
        self, mock_get, mock_get_device_identifier, mock_get_client_ip
    ):
        """
        Test that the middleware updates UserIP and UserDevice objects
        :param mock_get:
        :param mock_get_device_identifier:
        :param mock_get_client_ip:
        :return:
        """
        # Mock the response from the external API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "country": "CountryName",
            "region": "RegionName",
            "city": "CityName",
        }

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

        # Check that geolocation data is updated
        user_ip = UserIP.objects.get(user=self.user, ip_address="123.123.123.123")
        self.assertEqual(user_ip.country, "CountryName")
        self.assertEqual(user_ip.region, "RegionName")
        self.assertEqual(user_ip.city, "CityName")

    @patch("users.middleware.requests.get")
    def test_get_geolocation_data_failure(self, mock_get):
        """
        Test that get_geolocation_data returns an empty dict when the API call fails.
        """
        # Configure the mock to simulate an API failure
        mock_get.return_value.status_code = 404  # Simulate a failure response

        # Call the method with a sample IP
        ip = "123.123.123.123"
        result = self.middleware.get_geolocation_data(ip)

        # Assert that the result is an empty dictionary
        self.assertEqual(result, {})

        # Verify that the requests.get was called correctly
        mock_get.assert_called_once_with(f"https://ipinfo.io/{ip}/json", timeout=120)
