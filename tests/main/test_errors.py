from django.test import TestCase, RequestFactory
from main.views import BadRequestView, ServerErrorView
from django.http import HttpResponseBadRequest, HttpResponseServerError


class ErrorViewsTestCase(TestCase):
    """
    Test the error views: BadRequestView and ServerErrorView.
    """

    factory = RequestFactory()

    def check_view_response(
        self, view_class, expected_response_class, expected_status_code
    ) -> None:
        """
        Utility method to test the response of a given view class.
        """
        view = view_class.as_view()
        request = self.factory.get("/")
        response = view(request)
        self.assertIsInstance(response, expected_response_class)
        self.assertEqual(response.status_code, expected_status_code)

    def test_bad_request_view(self) -> None:
        """
        Ensure the BadRequestView returns a 400 Bad Request response.
        """
        self.check_view_response(BadRequestView, HttpResponseBadRequest, 400)

    def test_server_error_view(self) -> None:
        """
        Ensure the ServerErrorView returns a 500 Internal Server Error response.
        """
        self.check_view_response(ServerErrorView, HttpResponseServerError, 500)
