import logging
import smtplib
from contextlib import nullcontext
from importlib import import_module

from django.conf import settings
from django.core.mail import send_mail
from procrastinate.contrib.django import app
from resend.exceptions import ResendError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger("procrastinate")


def _email_delivery_context(debug_destinations):
    """Apply the queued test destinations for the duration of a local email send.

    Workers run outside the browser request, so they must restore the selection
    captured when the email was queued. The context resets it after the send.
    This helper lives beside the task to keep that worker setup in one place;
    production gets a no-op context without importing local debug modules.
    """
    if settings.DEBUG:
        return import_module("core.debug.email").email_debug_context(debug_destinations)
    return nullcontext()


@app.task()
def send_email_task(
    subject: str,
    message: str,
    from_email: str,
    recipient_list: list[str],
    debug_destinations: list[str] | None = None,
) -> bool:
    """
    A procrastinate task to send an email.

    :param subject: Subject of the email.
    :param message: Body of the email.
    :param from_email: Sender's email address.
    :param recipient_list: A list of recipient email addresses.
    :param debug_destinations: Test destinations captured when the email was queued.
    :return: True if the email is sent successfully, False otherwise.
    """
    with _email_delivery_context(debug_destinations):
        try:
            return send_mail(subject, message, from_email, recipient_list) > 0
        except (ResendError, smtplib.SMTPException) as e:
            logger.error(e)
            return False


def _email_queue_options():
    """Capture the current local test destinations as email task arguments.

    Passing a snapshot to the worker preserves this browser's selection even if
    it changes before the job runs. This helper lives beside the queue function
    because these options belong to the task handoff. Production returns no extra
    arguments and never imports local debug modules.
    """
    options = {}
    if settings.DEBUG:
        options["debug_destinations"] = import_module(
            "core.debug.email"
        ).get_debug_email_destinations()
    return options


def queue_email(subject, message, from_email, recipient_list):
    """Queue an email with a snapshot of this browser's development selection."""
    return send_email_task.defer(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        **_email_queue_options(),
    )


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
