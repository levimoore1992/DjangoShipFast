import logging
import smtplib

from django.conf import settings
from django.core.mail import send_mail
from procrastinate.contrib.django import app
from resend.exceptions import ResendError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger("procrastinate")


@app.task()
def send_email_task(
    subject: str, message: str, from_email: str, recipient_list: list[str]
) -> bool:
    """
    A procrastinate task to send an email.

    :param subject: Subject of the email.
    :param message: Body of the email.
    :param from_email: Sender's email address.
    :param recipient_list: A list of recipient email addresses.
    :return: True if the email is sent successfully, False otherwise.
    """
    try:
        return send_mail(subject, message, from_email, recipient_list) > 0
    except (ResendError, smtplib.SMTPException) as e:
        logger.error(e)
        return False


@app.task()
def send_slack_message(message: str) -> None:
    """Send a Slack message with @channel mention"""
    client = WebClient(token=settings.SLACK_BOT_TOKEN)
    try:
        client.chat_postMessage(
            channel=settings.SLACK_DEFAULT_CHANNEL, text=f"@channel {message}"
        )
    except SlackApiError as e:
        logger.error("Error sending Slack message: %s", e)
        raise


def notify_by_slack(message: str) -> None:
    """Queue a Slack notification"""

    if not settings.ENABLE_SLACK_MESSAGES:
        return

    send_slack_message.defer(message)
