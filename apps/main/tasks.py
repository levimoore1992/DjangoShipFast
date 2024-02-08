import logging
import smtplib

from celery import shared_task
from django.core.mail import send_mail

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
