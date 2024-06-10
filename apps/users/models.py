from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import CIEmailField
from django.db import models

from apps.main.mixins import CreateMediaLibraryMixin


class User(CreateMediaLibraryMixin, AbstractUser):
    """An override of the user model to extend any new fields or remove others."""

    # override the default email field so that we can make it unique
    email = CIEmailField(max_length=255, unique=True, verbose_name="Email Address")
    avatar = models.ImageField(upload_to="profile_image/", null=True, blank=True)

    # Add any custom fields for your application here

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def avatar_url(self):
        """Return the URL of the user's avatar."""
        if self.avatar:
            return self.avatar.url
        return "https://www.gravatar.com/avatar/"


class UserIPManager(models.Manager):
    """
    A custom manager for the UserIP model.
    """

    def is_ip_blocked_or_suspicious(self, ip_address):
        """
        Check if an IP address is blocked or suspicious.
        :param ip_address:
        :return:
        """
        return (
            self.filter(ip_address=ip_address, is_blocked=True).exists()
            or self.filter(ip_address=ip_address, is_suspicious=True).exists()
        )

    def get_ip_history_for_user(self, user_id):
        """
        Get the IP history for a user.
        :param user_id:
        :return:
        """
        return self.filter(user_id=user_id).order_by("-last_seen")


class UserIP(models.Model):
    """
    This Django model stores IP addresses associated with users.

    Attributes:
        user (User): ForeignKey to the User model.
        ip_address (str): Stores the IP address.
        last_seen (DateTime): Records the last time the IP was used.

    Edge Cases:
        - Users with dynamic IP addresses may generate multiple records.
        - VPN or proxy usage can mask true IP addresses.
        - IPv4 and IPv6 addresses are handled, but formatting differences are not considered.
    """

    objects = UserIPManager()

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ips", null=True, blank=True
    )
    ip_address = models.GenericIPAddressField()
    last_seen = models.DateTimeField(auto_now=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_suspicious = models.BooleanField(default=False)


class UserDeviceManager(models.Manager):
    """
    A custom manager for the UserDevice model.
    """

    def is_device_blocked(self, device_identifier):
        """
        Check if a device is blocked.
        :param device_identifier:
        :return:
        """
        return self.filter(
            device_identifier=device_identifier, is_blocked=True
        ).exists()

    def get_device_history_for_user(self, user_id):
        """
        Get the device history for a user.
        :param user_id:
        :return:
        """
        return self.filter(user_id=user_id).order_by("-last_seen")


class UserDevice(models.Model):
    """
    This Django model stores device identifiers associated with users.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="devices", null=True, blank=True
    )
    device_identifier = models.CharField(max_length=255)
    last_seen = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)

    objects = UserDeviceManager()
