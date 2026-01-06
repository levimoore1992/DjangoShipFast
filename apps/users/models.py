import auto_prefetch
import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Value, F
from django.db.models.functions import Concat
from django.templatetags.static import static
from django_lifecycle import LifecycleModelMixin, hook, AFTER_UPDATE

from procrastinate.contrib.django import app
from procrastinate.contrib.django.models import ProcrastinateJob

from apps.main.tasks import send_we_miss_you_email_task
from apps.main.mixins import CreateMediaLibraryMixin


class User(LifecycleModelMixin, CreateMediaLibraryMixin, AbstractUser):
    """An override of the user model to extend any new fields or remove others."""

    # override the default email field so that we can make it unique
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name="Email Address",
        db_collation="en-x-icu",
    )
    avatar = models.ImageField(upload_to="profile_image/", null=True, blank=True)

    full_name = models.GeneratedField(
        expression=Concat(
            F("first_name"),
            Value(" "),
            F("last_name"),
            output_field=models.CharField(),
        ),
        output_field=models.CharField(max_length=255),
        db_persist=True,
    )

    referral_source = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="How did you hear about us?",
    )

    # Add any custom fields for your application here

    def __str__(self):
        return self.email

    @hook(AFTER_UPDATE, when="last_login", has_changed=True)
    def schedule_we_miss_you_email(self):
        """
        Schedule a 'we miss you' email for X days from now when user logs in.

        If the user logs in again before the email is sent, this will
        reschedule the task by canceling the old one first.
        """

        days = settings.INACTIVE_USER_EMAIL_DAYS
        lock_key = f"we_miss_you_{self.id}"

        # Cancel any existing pending "we miss you" email for this user
        existing_jobs = ProcrastinateJob.objects.filter(
            queueing_lock=lock_key, status="todo"
        )
        for job in existing_jobs:
            app.job_manager.cancel_job_by_id(job.id, delete_job=True)

        # Schedule new email
        send_we_miss_you_email_task.configure(
            schedule_in={"days": days},
            queueing_lock=lock_key,
        ).defer(user_id=self.id)

    @property
    def avatar_url(self):
        """Return the URL of the user's avatar."""
        if self.avatar:
            return self.avatar.url
        return static("images/default_user.jpeg")

    def deactivate_user(self):
        """Does a soft delete of a user"""

        self.is_active = False
        self.save()

    def block_user(self):
        """Deactivate the user and block all devices and IP's"""
        self.deactivate_user()
        self.block_devices()
        self.block_ips()

    def block_devices(self):
        """Block all devices that are related to a user"""

        self.devices.all().update(is_blocked=True)

    def block_ips(self):
        """Block all ip addresses related to a user"""
        self.ips.all().update(is_blocked=True)


class UserIPManager(models.Manager):
    """
    A custom manager for the UserIP model.
    """

    def is_ip_blocked(self, ip_address):
        """Checks if the ip address is blocked"""
        return self.filter(ip_address=ip_address, is_blocked=True).exists()

    def is_ip_blocked_or_suspicious(self, ip_address):
        """
        Check if an IP address is blocked or suspicious.
        :param ip_address:
        :return:
        """
        return (
            self.is_ip_blocked(ip_address)
            or self.filter(ip_address=ip_address, is_suspicious=True).exists()
        )

    def get_ip_history_for_user(self, user_id):
        """
        Get the IP history for a user.
        :param user_id:
        :return:
        """
        return self.filter(user_id=user_id).order_by("-last_seen")


class UserIP(auto_prefetch.Model):
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

    user = auto_prefetch.ForeignKey(User, on_delete=models.CASCADE, related_name="ips")
    ip_address = models.GenericIPAddressField()
    last_seen = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    is_suspicious = models.BooleanField(default=False)

    @property
    def location(self):
        """
        Return the location of the user based off ipinfo
        """
        response = requests.get(f"https://ipinfo.io/{self.ip_address}/json", timeout=10)  # noqa
        if response.status_code == 200:
            json = response.json()
            return f"{json['country']}, {json['region']}, {json['city']}"
        return None


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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    device_identifier = models.CharField(max_length=255)
    last_seen = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)

    objects = UserDeviceManager()
