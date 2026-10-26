import smtplib
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase, override_settings
from resend.exceptions import ResendError
from slack_sdk.errors import SlackApiError

from apps.main.tasks import notify_by_slack, send_email_task, send_slack_message


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

    @patch("apps.main.tasks.send_mail", return_value=0)
    def test_send_email_not_delivered(self, mock_send_mail):
        """Do not report success when the backend sends no messages."""
        self.assertFalse(
            send_email_task("Subject", "Body", "from@example.com", ["to@example.com"])
        )
        mock_send_mail.assert_called_once()

    @patch("apps.main.tasks.send_mail")
    def test_resend_failure(self, mock_send_mail):
        """Keep the task's failure result when Resend rejects delivery."""
        mock_send_mail.side_effect = ResendError(
            code=429,
            error_type="rate_limit_exceeded",
            message="Too many requests",
            suggested_action="Try again later.",
        )

        self.assertFalse(
            send_email_task("Subject", "Body", "from@example.com", ["to@example.com"])
        )
        mock_send_mail.assert_called_once()

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


class SlackNotificationTests(TestCase):
    """Test suite for Slack notification functionality"""

    def setUp(self):
        """Set up test case with common test data"""
        super().setUp()
        self.message = "Test message"

    @patch("apps.main.tasks.WebClient")
    def test_send_slack_message(self, mock_webclient):
        """Test sending message to the default channel"""
        # Setup
        mock_client = Mock()
        mock_webclient.return_value = mock_client

        # Execute
        # Call the task directly, not through Celery
        send_slack_message(self.message)

        # Assert
        mock_webclient.assert_called_once_with(token=settings.SLACK_BOT_TOKEN)
        mock_client.chat_postMessage.assert_called_once_with(
            channel=settings.SLACK_DEFAULT_CHANNEL, text=f"@channel {self.message}"
        )

    @patch("apps.main.tasks.WebClient")
    @patch("apps.main.tasks.logger")
    def test_send_slack_message_handles_error(self, mock_logger, mock_webclient):
        """Test error handling when Slack API fails"""
        # Setup
        mock_client = Mock()
        error = SlackApiError(
            response=Mock(status_code=400, data={"error": "channel_not_found"}),
            message="Slack API error",
        )
        mock_client.chat_postMessage.side_effect = error
        mock_webclient.return_value = mock_client

        # Execute and Assert
        with self.assertRaises(SlackApiError):
            send_slack_message(self.message)

        # Verify the error was logged with the correct format
        mock_logger.error.assert_called_once_with(
            "Error sending Slack message: %s", error
        )

    @override_settings(ENABLE_SLACK_MESSAGES=True)
    @patch("apps.main.tasks.send_slack_message")
    def test_notify_by_slack(self, mock_send):
        """Test notify_by_slack queues task"""
        # Execute
        notify_by_slack(self.message)

        # Assert
        mock_send.defer.assert_called_once_with(self.message)
