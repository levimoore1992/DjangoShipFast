import logging
import smtplib

from django.conf import settings
from django.core.mail import send_mail

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from procrastinate.contrib.django import app

logger = logging.getLogger("procrastinate")


@app.task()
def send_email_task(
    subject: str, message: str, from_email: str, recipient_list: list[str]
) -> bool:
    """
    Sends an email asynchronously as a Procrastinate task.
    
    Args:
    	subject: The subject line of the email.
    	message: The body content of the email.
    	from_email: The sender's email address.
    	recipient_list: List of recipient email addresses.
    
    Returns:
    	True if the email was sent successfully; False if an SMTP error occurred.
    """
    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except smtplib.SMTPException as e:
        logger.error(e)
        return False


@app.task()
def send_slack_message(message: str) -> None:
    """
    Sends a message to the default Slack channel with an @channel mention.
    
    Attempts to post the provided message to the Slack channel specified in settings using the Slack WebClient. If sending fails due to a Slack API error, the exception is logged and re-raised.
    """
    client = WebClient(token=settings.SLACK_BOT_TOKEN)
    try:
        client.chat_postMessage(
            channel=settings.SLACK_DEFAULT_CHANNEL, text=f"@channel {message}"
        )
    except SlackApiError as e:
        logger.error("Error sending Slack message: %s", e)
        raise


def notify_by_slack(message: str) -> None:
    """
    Queues a Slack notification message if Slack messaging is enabled.
    
    If Slack messaging is disabled via settings, the function returns without queuing the message.
    """

    if not settings.ENABLE_SLACK_MESSAGES:
        return

    send_slack_message.defer(message)
