import smtplib
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings

from apps.main.tasks import notify_admins, send_email_task
from tests.factories.users import UserFactory


class TestSendEmailTask(TestCase):
    """
    Test the send_email_task.
    """

    @patch("apps.main.tasks.send_mail")
    def test_send_email_success(self, mock_send_mail):
        """
        Test the send_email_task successfully sends an email.
        """
        mock_send_mail.return_value = 1  # Simulate successful email send

        subject = "Test Subject"
        message = "Test message"
        from_email = "from@example.com"
        recipient_list = ["to@example.com"]

        task_result = send_email_task(subject, message, from_email, recipient_list)
        self.assertTrue(task_result)
        mock_send_mail.assert_called_once_with(
            subject, message, from_email, recipient_list
        )

    @patch("apps.main.tasks.send_mail")
    def test_send_email_failure(self, mock_send_mail):
        """
        Test the send_email_task handling a failure in sending an email.
        """
        mock_send_mail.side_effect = (
            smtplib.SMTPException
        )  # Simulate email send failure

        subject = "Test Subject"
        message = "Test message"
        from_email = "from@example.com"
        recipient_list = ["to@example.com"]

        task_result = send_email_task(subject, message, from_email, recipient_list)
        self.assertFalse(task_result)
        mock_send_mail.assert_called_once_with(
            subject, message, from_email, recipient_list
        )


@override_settings(ENABLE_EMAILS=True, DEFAULT_FROM_EMAIL="noreply@example.com")
class AdminNotificationTests(TestCase):
    """Verify notification recipients and delivery through the email task."""

    @patch("apps.main.tasks.send_email_task.defer")
    def test_only_active_superusers_receive_notifications(self, mock_defer):
        UserFactory(email="admin@example.com", is_superuser=True, is_staff=True)
        UserFactory(email="other-admin@example.com", is_superuser=True, is_staff=True)
        UserFactory(is_superuser=True, is_staff=True, is_active=False)
        UserFactory(is_staff=True)
        UserFactory()
        UserFactory(email="", is_superuser=True, is_staff=True)

        notify_admins("New contact request", "Test message")

        mock_defer.assert_called_once()
        kwargs = mock_defer.call_args.kwargs
        self.assertCountEqual(
            kwargs["recipient_list"], ["admin@example.com", "other-admin@example.com"]
        )
        self.assertEqual(kwargs["subject"], "New contact request")
        self.assertEqual(kwargs["message"], "Test message")
        self.assertEqual(kwargs["from_email"], "noreply@example.com")

    @patch("apps.main.tasks.send_email_task.defer")
    def test_no_admins_does_not_queue_email(self, mock_defer):
        UserFactory(is_staff=True)
        notify_admins("New contact request", "Test message")
        mock_defer.assert_not_called()

    @override_settings(ENABLE_EMAILS=False)
    @patch("apps.main.tasks.send_email_task.defer")
    def test_disabled_emails_do_not_queue_notifications(self, mock_defer):
        UserFactory(is_superuser=True, is_staff=True)
        notify_admins("New contact request", "Test message")
        mock_defer.assert_not_called()

    @override_settings(
        MAILERS={
            "default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}
        }
    )
    @patch("apps.main.tasks.send_email_task.defer", side_effect=send_email_task)
    def test_queued_notification_delivers_admin_email(self, mock_defer):
        UserFactory(email="admin@example.com", is_superuser=True, is_staff=True)
        notify_admins(
            "New social signup", "New user signing up via google: user@example.com"
        )
        mock_defer.assert_called_once()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["admin@example.com"])
        self.assertEqual(mail.outbox[0].subject, "New social signup")
        self.assertEqual(
            mail.outbox[0].body, "New user signing up via google: user@example.com"
        )
