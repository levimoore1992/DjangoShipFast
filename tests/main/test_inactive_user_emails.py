"""
Tests for the inactive user 'we miss you' email feature.
"""

from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.main.emails import send_we_miss_you_email
from apps.main.tasks import send_we_miss_you_email_task
from tests.factories.users import UserFactory


class SendWeMissYouEmailTestCase(TestCase):
    """Test cases for the send_we_miss_you_email function."""

    def setUp(self):
        self.user = UserFactory(
            email="testuser@example.com",
            first_name="John",
        )

    @patch("apps.main.emails.send_email_task")
    @override_settings(RAILWAY_HOST="example.com")
    def test_send_we_miss_you_email_success(self, mock_send_email):
        """Test successful email sending."""
        send_we_miss_you_email(self.user)

        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args

        self.assertEqual(
            call_args.kwargs["subject"], "We miss you! Come back and see what's new"
        )
        self.assertEqual(call_args.kwargs["recipient_list"], ["testuser@example.com"])
        self.assertIn("John", call_args.kwargs["message"])

    @patch("apps.main.emails.send_email_task")
    @override_settings(RAILWAY_HOST=None)
    def test_send_we_miss_you_email_localhost_fallback(self, mock_send_email):
        """Test that localhost is used when RAILWAY_HOST is not set."""
        send_we_miss_you_email(self.user)

        call_args = mock_send_email.call_args
        self.assertIn("https://localhost:8000", call_args.kwargs["message"])

    @patch("apps.main.emails.send_email_task")
    @override_settings(RAILWAY_HOST="mysite.railway.app")
    def test_send_we_miss_you_email_https_prefix(self, mock_send_email):
        """Test that https is added to site URL."""
        send_we_miss_you_email(self.user)

        call_args = mock_send_email.call_args
        self.assertIn("https://mysite.railway.app", call_args.kwargs["message"])


class SendWeMissYouEmailTaskTestCase(TestCase):
    """Test cases for the Procrastinate task."""

    def setUp(self):
        self.user = UserFactory(
            email="taskuser@example.com",
            first_name="Jane",
        )

    @patch("apps.main.emails.send_email_task")
    def test_task_sends_email_to_active_user(self, mock_send_email):
        """Test that task sends email to active user."""
        send_we_miss_you_email_task(self.user.id)

        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        self.assertEqual(call_args.kwargs["recipient_list"], ["taskuser@example.com"])

    @patch("apps.main.emails.send_email_task")
    def test_task_skips_inactive_user(self, mock_send_email):
        """Test that task skips inactive users."""
        self.user.is_active = False
        self.user.save()

        send_we_miss_you_email_task(self.user.id)

        mock_send_email.assert_not_called()

    @patch("apps.main.emails.send_email_task")
    def test_task_handles_missing_user(self, mock_send_email):
        """Test that task handles non-existent user gracefully."""
        send_we_miss_you_email_task(99999)

        mock_send_email.assert_not_called()


class UserLifecycleHookTestCase(TestCase):
    """Test cases for the django-lifecycle hook on User model."""

    def setUp(self):
        self.user = UserFactory(email="hookuser@example.com")

    @patch("apps.main.tasks.send_we_miss_you_email_task")
    @override_settings(INACTIVE_USER_EMAIL_DAYS=10)
    def test_last_login_change_schedules_email(self, mock_task):
        """Test that updating last_login schedules the email task."""
        mock_configured = MagicMock()
        mock_task.configure.return_value = mock_configured

        # Update last_login to trigger the hook
        self.user.last_login = timezone.now()
        self.user.save()

        mock_task.configure.assert_called_once_with(
            schedule_in={"days": 10}, queueing_lock=f"we_miss_you_{self.user.id}"
        )
        mock_configured.defer.assert_called_once_with(user_id=self.user.id)

    @patch("apps.main.tasks.send_we_miss_you_email_task")
    @override_settings(INACTIVE_USER_EMAIL_DAYS=14)
    def test_custom_days_setting(self, mock_task):
        """Test that custom days setting is respected."""
        mock_configured = MagicMock()
        mock_task.configure.return_value = mock_configured

        self.user.last_login = timezone.now()
        self.user.save()

        mock_task.configure.assert_called_once_with(
            schedule_in={"days": 14}, queueing_lock=f"we_miss_you_{self.user.id}"
        )

    @patch("apps.main.tasks.send_we_miss_you_email_task")
    def test_other_field_changes_dont_trigger_hook(self, mock_task):
        """Test that changing other fields doesn't schedule email."""
        self.user.first_name = "NewName"
        self.user.save()

        mock_task.configure.assert_not_called()
