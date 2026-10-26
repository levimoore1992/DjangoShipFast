"""Middleware registered only by local development settings."""

from django.conf import settings

from core.debug.email import (
    DEBUG_EMAIL_SESSION_KEY,
    override_debug_email_destinations,
)


def debug_email_middleware(get_response):
    """Bind the browser's saved destinations for the duration of a request."""

    def middleware(request):
        if not settings.DEBUG:
            return get_response(request)
        destinations = request.session.get(DEBUG_EMAIL_SESSION_KEY)
        with override_debug_email_destinations(destinations):
            return get_response(request)

    return middleware
