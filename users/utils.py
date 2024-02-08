import hashlib

from django.conf import settings
from django.contrib.auth import get_user_model

from main.tasks import send_email_task


from .models import UserDevice, UserIP


User = get_user_model()


def block_user_and_devices(user_id):
    """
    Blocks a user and all associated devices, and handles their IP addresses.

    Args:
    user_id (int): The ID of the user to be blocked.

    Returns:
    None
    """
    # Block the user
    User.objects.filter(id=user_id).update(is_active=False)

    # Block all devices associated with the user
    UserDevice.objects.filter(user_id=user_id).update(is_blocked=True)

    # Handle IPs used by the user
    user_ips = UserIP.objects.filter(user=user_id)
    for ip in user_ips:
        mark_ip_as_suspicious(ip.ip_address)

    # Send email to user that they are blocked
    send_email_task.delay(
        subject="Your account has been blocked",
        message="Your account has been blocked. Please contact support for more information.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[User.objects.get(id=user_id).email],
    )


def mark_ip_as_suspicious(ip_address):
    """
    Marks an IP address as suspicious.

    Args:
    ip_address (str): The IP address to mark as suspicious.

    Returns:
    None
    """
    UserIP.objects.filter(ip_address=ip_address).update(is_suspicious=True)


def block_ip(ip_address):
    """
    Blocks an IP address.

    Args:
    ip_address (str): The IP address to block.

    Returns:
    None
    """
    UserIP.objects.filter(ip_address=ip_address).update(is_blocked=True)


def get_device_identifier(request):
    """
    Generates a unique device identifier based on request headers.

    This method uses a combination of HTTP headers to create a hash
    that serves as a unique identifier for the user's device.

    Returns:
        str: A hashed string representing the device identifier.
    """

    user_agent = request.META.get("HTTP_USER_AGENT", "")
    accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

    # You can include more headers as needed for better uniqueness
    raw_string = user_agent + accept_language

    # Hashing for privacy and consistency
    hashed_string = hashlib.sha256(raw_string.encode()).hexdigest()

    return hashed_string
