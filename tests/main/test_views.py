from django.test import TestCase
from django.urls import reverse

from main.consts import ContactType
from main.forms import ContactForm
from main.models import Contact
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


class ContactUsViewTests(TestCase):
    """
    Unit tests for the ContactUsView.
    """

    def setUp(self):
        super().setUp()
        self.url = reverse("contact_us")

    def test_get_contact_form(self):
        # Use the client to make a GET request
        response = self.client.get(self.url)

        # Assert that the response has a 200 OK status
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains an empty form
        self.assertIsInstance(response.context["form"], ContactForm)
        self.assertFalse(response.context["form"].is_bound)

    def test_post_valid_contact_form(self):
        # Prepare some valid form data
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Test subject",
            "message": "Hello, this is a test message.",
            "type": ContactType.GENERAL.value,
        }

        # Use the client to make a POST request with the form data
        response = self.client.post(self.url, form_data)

        # Assert that the form was valid and the contact was created
        self.assertEqual(Contact.objects.count(), 1)

        # Assert that the user was redirected to the "home" URL
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_post_invalid_contact_form(self):
        # Prepare some invalid form data (e.g., missing name and invalid email format)
        form_data = {
            "email": "invalid_email",
            "subject": "Test subject",
            "message": "Hello, this is a test message.",
            "type": ContactType.GENERAL.value,
        }

        # Use the client to make a POST request with the form data
        response = self.client.post(self.url, form_data)

        # Assert that the form was not valid and no contact was created
        self.assertEqual(Contact.objects.count(), 0)

        # Assert that the user saw the form with errors
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].is_bound)
        self.assertFalse(response.context["form"].is_valid())
