import logging
import smtplib

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from celery import shared_task

from django.conf import settings
from django.core.mail import send_mail

from apps.main.bot import discord_bot

logger = logging.getLogger("celery")


@shared_task
def send_email_task(
    subject: str, message: str, from_email: str, recipient_list: list[str]
) -> bool:
    """
    A Celery task to send an email.

    :param subject: Subject of the email.
    :param message: Body of the email.
    :param from_email: Sender's email address.
    :param recipient_list: A list of recipient email addresses.
    :return: True if the email is sent successfully, False otherwise.
    """
    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except smtplib.SMTPException as e:
        logger.error(e)
        return False


@shared_task(
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(SlackApiError,),
    retry_backoff=True,
)
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
    send_slack_message.delay(message)


@shared_task
def send_discord_announcement(message=None, channel_id=None, embed=None):
    """
    Celery task to send an announcement to a Discord channel.

    Args:
        message (str, optional): Plain text message
        channel_id (str): Channel ID to send to
        embed (dict, optional): Embed configuration

    Returns:
        bool: Success status
    """

    return discord_bot.send_announcement(message, channel_id, embed)


def create_discord_announcement(message=None, channel_id=None, embed=None):
    """
    Wrapper function that handles calling the Celery task

    This ensures the task is always called with .delay() consistently
    """
    send_discord_announcement.delay(
        message=message,
        channel_id=channel_id,
        embed=embed,
    )
