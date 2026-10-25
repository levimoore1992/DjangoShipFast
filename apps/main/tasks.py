import logging
import smtplib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from procrastinate.contrib.django import app

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
        send_mail(subject, message, from_email, recipient_list)
        return True
    except smtplib.SMTPException as e:
        logger.error(e)
        return False


def notify_admins(subject: str, message: str) -> None:
    """Queue an email notification to active superusers."""
    if not settings.ENABLE_EMAILS:
        return

    recipients = list(
        get_user_model()
        .objects.filter(is_active=True, is_superuser=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    if recipients:
        send_email_task.defer(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
        )
