from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from apps.main.consts import ContactType
from apps.main.forms import ContactForm
from apps.main.models import (
    Contact,
    TermsAndConditions,
    PrivacyPolicy,
    Report,
    Notification,
)
from tests.factories.main import NotificationFactory
from tests.factories.users import UserFactory


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
        """
        Test that the contact form is displayed.
        :return: None
        """
        # Use the client to make a GET request
        response = self.client.get(self.url)

        # Assert that the response has a 200 OK status
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains an empty form
        self.assertIsInstance(response.context["form"], ContactForm)
        self.assertFalse(response.context["form"].is_bound)

    def test_post_valid_contact_form(self):
        """
        Test that a valid contact form is submitted successfully.
        :return: None
        """
        # Prepare some valid form data
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Test subject",
            "message": "Hello, this is a test message.",
            "type": ContactType.GENERAL.value,
            "g-recaptcha-response": "PASSED",
        }

        # Use the client to make a POST request with the form data
        response = self.client.post(self.url, form_data)

        # Assert that the form was valid and the contact was created
        self.assertEqual(Contact.objects.count(), 1)

        # Assert that the user was redirected to the "home" URL
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_post_invalid_contact_form(self):
        """
        Test that an invalid contact form is not submitted.
        :return:
        """
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


class TermsAndConditionsViewTests(TestCase):
    """
    Unit tests for the TermsAndConditionsView.
    """

    def setUp(self):
        super().setUp()
        self.url = reverse("terms_and_conditions")

    def test_get_terms_and_conditions(self):
        """
        Test that the terms and conditions are displayed.
        :return: None
        """
        TermsAndConditions.objects.create(
            terms="This is a test terms and conditions page."
        )
        # Use the client to make a GET request
        response = self.client.get(self.url)

        # Assert that the response has a 200 OK status
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the terms and conditions
        self.assertContains(response, "This is a test terms and conditions page.")


class PrivacyPolicyViewTests(TestCase):
    """
    Unit tests for the PrivacyPolicyView.
    """

    def setUp(self):
        super().setUp()
        self.url = reverse("privacy_policy")

    def test_get_privacy_policy(self):
        """
        Test that the privacy policy is displayed.

        :return:
        """
        PrivacyPolicy.objects.create(policy="This is a test privacy policy page.")
        # Use the client to make a GET request
        response = self.client.get(self.url)

        # Assert that the response has a 200 OK status
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the privacy policy
        self.assertContains(response, "This is a test privacy policy page.")


class ReportViewTest(TestCase):
    """
    Test cases for the ReportView.
    """

    def setUp(self):
        """
        Set up the test case with a reporter and a notification to report.
        :return:
        """
        super().setUp()
        self.reporter = UserFactory()
        self.client.force_login(self.reporter)

        self.reported_notification = NotificationFactory()
        # Correctly reference ContentType model name as expected by the view
        self.model_name = ContentType.objects.get_for_model(Notification).model
        self.object_id = self.reported_notification.pk
        self.report_url = reverse("report", args=[self.model_name, self.object_id])

        content_type = ContentType.objects.get_for_model(Notification)
        self.model_type = f"{content_type.app_label}_{content_type.model}"

    def test_report_creation(self):
        """
        Test report is created successfully for a Notification object.
        """
        post_data = {"reason": "Inappropriate content"}
        response = self.client.post(self.report_url, post_data)

        self.assertEqual(response.status_code, 302)  # Expecting redirect
        exists = Report.objects.filter(
            content_type=ContentType.objects.get(model=self.model_name),
            object_id=self.object_id,
            reporter=self.reporter,
            reason=post_data["reason"],
        ).exists()
        self.assertTrue(exists)

    def test_redirect_after_report(self):
        """
        Test user is redirected correctly after reporting.
        """
        post_data = {"reason": "Inappropriate content"}

        # Case 1: With HTTP_REFERER
        referer_url = "/some-page/"
        response = self.client.post(
            self.report_url, post_data, HTTP_REFERER=referer_url
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, referer_url)

        # Case 2: Without HTTP_REFERER (should redirect to "home")
        response = self.client.post(self.report_url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "home")

    def test_report_creation_with_invalid_object_id(self):
        """
        Test report creation with an invalid object ID.
        """
        # Use an object ID that doesn't exist
        invalid_object_id = self.reported_notification.pk + 1

        post_data = {"reason": "Inappropriate content"}
        report_url = reverse("report", args=[self.model_name, invalid_object_id])
        response = self.client.post(report_url, post_data)

        # Expecting a 404 response since the object doesn't exist
        self.assertEqual(response.status_code, 404)

        # Check that no report was created
        exists = Report.objects.filter(
            content_type=ContentType.objects.get(model=self.model_name),
            object_id=invalid_object_id,
            reporter=self.reporter,
            reason=post_data["reason"],
        ).exists()
        self.assertFalse(exists)
