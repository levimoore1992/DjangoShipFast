from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from auditlog.registry import auditlog

from main.models import (
    TermsAndConditions,
    PrivacyPolicy,
    Contact,
    AuditLogConfig,
    Notification,
    SocialMediaLink,
)

from tests.factories.main import NotificationFactory, SocialMediaLinkFactory, FAQFactory
from tests.factories.users import UserFactory


class TermsAndConditionsTest(TestCase):
    """
    Test the TermsAndConditions model.
    """

    def test_creation_and_str(self):
        """
        Test the creation and string representation of the TermsAndConditions model.
        :return:
        """
        terms = TermsAndConditions.objects.create(terms="Sample Terms")
        self.assertTrue(isinstance(terms, TermsAndConditions))
        self.assertEqual(
            str(terms), f"Terms And Conditions created at {terms.created_at}"
        )


class PrivacyPolicyTest(TestCase):
    """
    Test the PrivacyPolicy model.
    """

    def test_creation_and_str(self):
        """
        Test the creation and string representation of the PrivacyPolicy model.
        :return:
        """
        policy = PrivacyPolicy.objects.create(policy="Sample Policy")
        self.assertTrue(isinstance(policy, PrivacyPolicy))
        self.assertEqual(str(policy), f"Privacy Policy created at {policy.created_at}")


class ContactTest(TestCase):
    """
    Test the Contact model.
    """

    def test_creation_and_str(self):
        """
        Test the creation and string representation of the Contact model.
        :return:
        """
        contact = Contact.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Test Subject",
            message="Test Message",
            type="General",
        )
        self.assertTrue(isinstance(contact, Contact))
        self.assertEqual(str(contact), "John Doe - Test Subject")


class AuditLogConfigTest(TestCase):
    """
    Test the AuditLogConfig model.
    """

    def setUp(self):
        self.model_name = "auth.User"
        self.audit_config = AuditLogConfig.objects.create(model_name=self.model_name)

        self.invalid_model_name = "invalid.Model"
        self.audit_config_invalid = AuditLogConfig.objects.create(
            model_name=self.invalid_model_name
        )

    def test_creation_and_str(self):
        """
        Test the creation and string representation of the AuditLogConfig model.
        """
        self.assertTrue(isinstance(self.audit_config, AuditLogConfig))
        self.assertEqual(str(self.audit_config), self.model_name)

    def test_register_and_unregister_model(self):
        """
        Test the registration and unregistration of a model with django-auditlog.
        """
        # Test register_model
        self.audit_config.register_model()
        self.assertIn(User, auditlog.get_models())

        # Test unregister_model
        self.audit_config.unregister_model()
        self.assertNotIn(User, auditlog.get_models())

    def test_register_model_with_invalid_model(self):
        """
        Test the register_model method with an invalid model name.
        """
        with patch("django.apps.apps.get_model", side_effect=LookupError):
            # No exception should be raised
            self.audit_config_invalid.register_model()

    def test_unregister_model_with_invalid_model(self):
        """
        Test the unregister_model method with an invalid model name.
        """
        with patch("django.apps.apps.get_model", side_effect=LookupError):
            # No exception should be raised
            self.audit_config_invalid.unregister_model()


class NotificationTest(TestCase):
    """
    Test the Notification model.
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.notification = NotificationFactory(
            title="Test Notification", user=self.user
        )

    def test_creation_and_str(self):
        """
        Test the creation and string representation of the Notification model.
        """
        self.assertTrue(isinstance(self.notification, Notification))
        self.assertEqual(str(self.notification), "Test Notification")

    def test_get_absolute_url(self):
        """
        Test the get_absolute_url method of the Notification model.
        """
        expected_url = reverse(
            "mark_as_read_and_redirect",
            kwargs={
                "notification_id": self.notification.pk,
                "destination_url": self.notification.link,
            },
        )
        self.assertEqual(self.notification.get_absolute_url(), expected_url)

    def test_mark_as_read(self):
        """
        Test the mark_as_read method of the Notification model.
        """
        self.assertFalse(self.notification.is_read)
        self.notification.mark_as_read()
        self.assertTrue(self.notification.is_read)


class SocialMediaLinkTest(TestCase):
    """
    Test the SocialMediaLink model.
    """

    def test_create_social_media_link(self):
        """
        Test the creation of a SocialMediaLink instance.
        """

        social_media_link = SocialMediaLinkFactory()

        # Fetch the created instance from the database
        fetched_social_media_link = SocialMediaLink.objects.get(id=social_media_link.id)

        # Test instance creation
        self.assertEqual(
            fetched_social_media_link.platform_name, social_media_link.platform_name
        )
        self.assertEqual(
            fetched_social_media_link.profile_url, social_media_link.profile_url
        )
        self.assertTrue(fetched_social_media_link.image)

    def test_string_representation(self):
        """
        Test the string representation of a SocialMediaLink instance.
        """
        social_media_link = SocialMediaLinkFactory(platform_name="TestPlatform")
        self.assertEqual(str(social_media_link), "TestPlatform link")

    def test_auto_timestamps(self):
        """
        Test the auto timestamps of a SocialMediaLink instance.
        """
        social_media_link = SocialMediaLinkFactory()
        self.assertIsNotNone(social_media_link.created_at)
        self.assertIsNotNone(social_media_link.updated_at)


class TestFAQ(TestCase):
    """
    Test the FAQ model.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.faq = FAQFactory()

    def test_string_representation(self):
        """
        Test the string representation of the FAQ model.
        """
        self.assertEqual(str(self.faq), self.faq.question)
