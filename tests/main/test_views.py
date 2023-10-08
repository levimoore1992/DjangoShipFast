from django.test import TestCase
from django.urls import reverse

from tests.main.factories import NotificationFactory


class MarkAsReadAndRedirectViewTestCase(TestCase):
    """
    Test cases for the MarkAsReadAndRedirectView.
    """

    def setUp(self) -> None:
        super().setUp()
        self.notification = NotificationFactory()
        self.url = reverse(
            "mark_as_read_and_redirect",
            kwargs={
                "notification_id": self.notification.id,
                "destination_url": self.notification.link,
            },
        )

    def test_notification_marked_as_read_and_redirected(self):
        """
        Test that a GET request marks the notification as read
        and redirects to the destination URL.
        """
        response = self.client.get(self.url)
        self.notification.refresh_from_db()  # Refresh the instance from the DB

        self.assertTrue(self.notification.is_read)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.notification.link)

    def test_non_matching_link(self):
        """
        Test if the view returns a 404 when the ID exists but the link doesn't match.

        This is to prevent malicious users from sending redirect links to other pages
        """
        url = reverse(
            "mark_as_read_and_redirect",
            kwargs={
                "notification_id": self.notification.id,
                "destination_url": "some_random_non_matching_url.com",
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
