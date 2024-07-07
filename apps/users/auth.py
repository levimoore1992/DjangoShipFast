import logging
from typing import Optional, Any

from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

from apps.users.models import User

logger = logging.getLogger("admin")


class DjangoAdminAuthBackend(ModelBackend):
    """
    Custom authentication backend for handling SSO email authentication.
    """

    def authenticate(
        self,
        request: Optional[HttpRequest],
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any
    ) -> Optional[User]:
        """
        Authenticates a user based on the SSO email.

        Args:
            request (Optional[HttpRequest]): The HTTP request object.
            username (Optional[str]): The username, not used in this backend.
            password (Optional[str]): The password, not used in this backend.
            kwargs (Any): Additional keyword arguments.

        Returns:
            Optional[User]: The authenticated user, or None if authentication failed.
        """
        # Extract the SSO email from kwargs
        sso_email = kwargs.get("sso_email")

        # If sso_email is not provided, this backend cannot handle the request
        if sso_email is None:
            return None

        try:
            # Look up a staff user by the email address
            return User.objects.get(is_staff=True, is_active=True, email=sso_email)
        except User.DoesNotExist:
            logger.error(
                "A user that did not have access to the site attempted to access it. %s",
                sso_email,
            )

            msg = (
                "Your email address does not have access to this site. "
                "Please contact a YourAppName administrator to fix this issue."
            )

            messages.error(request, msg)
            return None
