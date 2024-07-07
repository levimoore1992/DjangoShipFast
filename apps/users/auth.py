import logging

from django.contrib import messages
from django.contrib.auth.backends import ModelBackend

from apps.users.models import User

logger = logging.getLogger("admin")


class DjangoAdminAuthBackend(ModelBackend):
    "Authenticate users from Google via single sign on"

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id, is_active=True, is_staff=True)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, sso_email=None, **kwargs):
        # admin_sso sends the user's google email address as "sso_email"
        # if it's not provided, this backend cannot handle the request
        # so return None immediately.
        if sso_email is None:
            return None

        try:
            # lookup a staff user by the email address
            return User.objects.get(is_staff=True, is_active=True, email=sso_email)
        except User.DoesNotExist:
            logger.error(
                f"A user that did not have access to the site attempted to access it. {sso_email}"
            )
            msg = (
                "Your email address does not have access to this site. "
                "Please contact a Languageloom administrator to fix this issue."
            )
            messages.error(request, msg)
            return None