from django.db import models
from django.urls import reverse

from users.models import User


class Notification(models.Model):
    """
    Notification model to handle user notifications.

    Attributes:
        user (User): The user to whom the notification belongs.
        title (str): The title of the notification.
        message (str): The message content of the notification.
        link (str): The URL to which the notification redirects.
        is_read (bool): Flag to check if the notification has been read.
        created_at (DateTimeField): The time the notification was created.
        updated_at (DateTimeField): The time the notification was last updated.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    TYPES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("danger", "Danger"),
        ("success", "Success"),
    ]
    type = models.CharField(max_length=10, choices=TYPES, default="info")

    def get_absolute_url(self) -> str:
        """
        Get the URL that allows users to mark the notification as read
        and be redirected to the destination URL.

        The link is URL-encoded to safely include it as a URL parameter.

        :return: URL as a string
        """
        return reverse(
            "mark_as_read_and_redirect",
            kwargs={"notification_id": self.pk, "destination_url": self.link},
        )

    def mark_as_read(self) -> None:
        """
        Mark the notification as read.
        """
        self.is_read = True
        self.save()

    def __str__(self) -> str:
        return self.title
