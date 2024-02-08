from unittest.mock import patch

from django.contrib.messages import get_messages
from django.http import HttpRequest
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.utils import timezone

from apps.main.consts import ContactStatus
from apps.main.models import TermsAndConditions, AuditLogConfig, Contact
from apps.main.admin import AuditLogConfigAdmin, ContactAdmin, TermsAndConditionsAdmin
from tests.factories.main import ContactFactory
from tests.factories.users import UserFactory


class TermsAndConditionsAdminTest(TestCase):
    """
    Test suite for the TermsAndConditionsAdmin class.
    """

    def setUp(self):
        """
        Set up the test suite.
        :return:
        """
        super().setUp()
        self.request_factory = RequestFactory()
        self.superuser = UserFactory(is_superuser=True)
        self.regular_user = UserFactory()
        self.terms_and_conditions = TermsAndConditions.objects.create(terms="test")

    def create_mock_request(self, user):
        """
        Create a mock request with the given user.
        :param user:
        :return:
        """
        request = self.request_factory.get("/fake-url")
        request.user = user
        return request

    def test_get_readonly_fields_with_superuser(self):
        """
        Test the get_readonly_fields method with a superuser.
        :return:
        """
        request = self.create_mock_request(self.superuser)
        admin = TermsAndConditionsAdmin(TermsAndConditions, None)
        readonly_fields = admin.get_readonly_fields(request, self.terms_and_conditions)
        self.assertEqual(readonly_fields, admin.readonly_fields)

    def test_get_readonly_fields_with_regular_user(self):
        """
        Test the get_readonly_fields method with a regular user.
        :return:
        """
        request = self.create_mock_request(self.regular_user)
        admin = TermsAndConditionsAdmin(TermsAndConditions, None)
        readonly_fields = admin.get_readonly_fields(request, self.terms_and_conditions)
        self.assertIn("terms", readonly_fields)


class AuditLogConfigAdminTest(TestCase):
    """
    Test suite for the AuditLogConfigAdmin class.
    """

    def setUp(self):
        self.site = AdminSite()
        self.user = UserFactory(is_superuser=True)
        self.admin = AuditLogConfigAdmin(AuditLogConfig, self.site)

    @patch("apps.main.models.AuditLogConfig.register_model")
    def test_save_model(self, mock_register_model):
        """
        Test the save_model method of AuditLogConfigAdmin.
        :param mock_register_model:
        :return:
        """
        request = HttpRequest()
        request.user = self.user
        obj = AuditLogConfig(model_name="YourModelName")

        self.admin.save_model(request, obj, None, None)

        mock_register_model.assert_called_once()

    @patch("apps.main.models.AuditLogConfig.unregister_model")
    def test_delete_model(self, mock_unregister_model):
        """
        Test the delete_model method of AuditLogConfigAdmin.
        :param mock_unregister_model:
        :return:
        """
        request = HttpRequest()
        request.user = self.user
        obj = AuditLogConfig.objects.create(model_name="YourModelName")

        self.admin.delete_model(request, obj)

        mock_unregister_model.assert_called_once()


class ContactAdminTest(TestCase):
    """
    Test suite for the ContactAdmin class.
    """

    def setUp(self):
        self.site = AdminSite()
        self.admin = ContactAdmin(Contact, self.site)
        self.user = UserFactory.create(is_superuser=True, is_staff=True)
        self.client.force_login(self.user)
        self.contact = ContactFactory()

        self.change_url = reverse("admin:main_contact_change", args=[self.contact.id])

    def test_response_change(self):
        """
        Test the response_change method of ContactAdmin.
        """
        status_key = f"_{ContactStatus.RESOLVED.value.lower().replace(' ', '_')}"
        response = self.client.post(self.change_url, {status_key: "1"}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.status, ContactStatus.RESOLVED.value)
        self.assertIsNotNone(self.contact.resolved_date)

        # Check if success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                f"Contact request marked as {ContactStatus.RESOLVED.value}"
                in message.message
                for message in messages
            )
        )

    def test_response_change_to_pending(self):
        """
        Test the response_change method of ContactAdmin when changing the contact status to PENDING.
        """
        contact = ContactFactory(
            status=ContactStatus.RESOLVED.value
        )  # Assuming initial status is different from PENDING
        self.change_url = reverse("admin:main_contact_change", args=[contact.id])

        status_key = "_pending"
        response = self.client.post(self.change_url, {status_key: "1"}, follow=True)

        self.assertEqual(response.status_code, 200)
        contact.refresh_from_db()
        self.assertEqual(contact.status, ContactStatus.PENDING.value)
        self.assertIsNone(
            contact.resolved_date
        )  # The resolved_date should be reset when status changes to PENDING

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                f"Contact request marked as {ContactStatus.PENDING.value}"
                in message.message
                for message in messages
            )
        )

    def test_response_change_to_in_progress(self):
        """
        Test the response_change method of ContactAdmin when changing the contact status to IN_PROGRESS.
        """
        contact = ContactFactory()  # Assuming initial status is PENDING or another
        self.change_url = reverse("admin:main_contact_change", args=[contact.id])

        status_key = "_in_progress"
        response = self.client.post(self.change_url, {status_key: "1"}, follow=True)

        self.assertEqual(response.status_code, 200)
        contact.refresh_from_db()
        self.assertEqual(contact.status, ContactStatus.IN_PROGRESS.value)
        self.assertIsNone(
            contact.resolved_date
        )  # The resolved_date should not be set for IN_PROGRESS

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                f"Contact request marked as {ContactStatus.IN_PROGRESS.value}"
                in message.message
                for message in messages
            )
        )

    def test_invalid_status_change(self):
        """
        Test the response_change method with an invalid status change.
        """
        contact = ContactFactory()
        invalid_status_key = "_invalid_status"
        response = self.client.post(
            self.change_url, {invalid_status_key: "1"}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        contact.refresh_from_db()
        self.assertEqual(
            contact.status, ContactStatus.PENDING.value
        )  # Assuming PENDING is the default status

        # Check that no success message for invalid status
        messages = list(get_messages(response.wsgi_request))
        self.assertFalse(
            any("Contact request marked as" in message.message for message in messages)
        )

    def test_response_change_to_closed(self):
        """
        Test the response_change method of ContactAdmin when changing the contact status to CLOSED.
        """
        contact = ContactFactory()  # Assuming initial status is PENDING or another
        self.change_url = reverse("admin:main_contact_change", args=[contact.id])

        status_key = "_closed"
        response = self.client.post(self.change_url, {status_key: "1"}, follow=True)

        self.assertEqual(response.status_code, 200)
        contact.refresh_from_db()
        self.assertEqual(contact.status, ContactStatus.CLOSED.value)
        self.assertIsNone(
            contact.resolved_date
        )  # The resolved_date should not be set for CLOSED

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                f"Contact request marked as {ContactStatus.CLOSED.value}"
                in message.message
                for message in messages
            )
        )

    def test_change_status_from_resolved_to_other_resets_resolved_date(self):
        """
        Test that changing status from RESOLVED to another status resets the resolved_date.
        """
        # Create a contact with RESOLVED status and a set resolved_date
        resolved_date = timezone.now()
        contact = ContactFactory(
            status=ContactStatus.RESOLVED.value, resolved_date=resolved_date
        )
        self.change_url = reverse("admin:main_contact_change", args=[contact.id])

        # Choose a different status (e.g., PENDING)
        new_status = ContactStatus.PENDING
        status_key = f"_{new_status.value.lower().replace(' ', '_')}"
        response = self.client.post(self.change_url, {status_key: "1"}, follow=True)

        self.assertEqual(response.status_code, 200)
        contact.refresh_from_db()
        self.assertEqual(contact.status, new_status.value)
        self.assertIsNone(contact.resolved_date)  # Check if resolved_date is reset

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                f"Contact request marked as {new_status.value}" in message.message
                for message in messages
            )
        )
