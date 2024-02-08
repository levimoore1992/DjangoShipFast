import smtplib
from unittest.mock import patch

from django.test import TestCase
from apps.main.tasks import send_email_task


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
