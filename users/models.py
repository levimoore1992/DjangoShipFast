from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # override the default email field so that we can make it unique
    email = models.EmailField(
        max_length=255, unique=True, verbose_name="Email Address", db_collation="nocase"
    )

    # Add any custom fields for your application here

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
