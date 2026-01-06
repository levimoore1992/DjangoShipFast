from django.conf import settings
from django.template.loader import render_to_string

import resend


resend.api_key = settings.RESEND_API_KEY


def send_email_task(
    subject: str,
    message: str,
    recipient_list: list[str],
) -> None:
    """
    :param subject: Subject of the email.
    :param message: Body of the email.
    :param recipient_list: A list of recipient email addresses.
    """

    if not settings.ENABLE_EMAILS:
        return None

    if settings.DEBUG:
        # override the recipient list on local development
        recipient_list = ["delivered@resend.dev"]

    params: resend.Emails.SendParams = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": recipient_list,
        "subject": subject,
        "html": message,
    }

    resend.Emails.send(params)

    return None


def send_we_miss_you_email(user) -> None:
    """
    Send a 'we miss you' email to an inactive user.

    :param user: The User object to send the email to.
    """
    site_url = settings.RAILWAY_HOST or "https://localhost:8000"
    if site_url and not site_url.startswith("http"):
        site_url = f"https://{site_url}"

    context = {
        "user": user,
        "site_url": site_url,
    }

    message = render_to_string("emails/we_miss_you.html", context)

    send_email_task(
        subject="We miss you! Come back and see what's new",
        message=message,
        recipient_list=[user.email],
    )
