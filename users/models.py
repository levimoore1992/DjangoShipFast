from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import CIEmailField


class User(AbstractUser):
    """An override of the user model to extend any new fields or remove others."""

    # override the default email field so that we can make it unique
    email = CIEmailField(max_length=255, unique=True, verbose_name="Email Address")

    # Add any custom fields for your application here

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
