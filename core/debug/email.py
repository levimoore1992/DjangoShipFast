"""Browser-scoped email test destinations, independent of Debug Toolbar."""

from contextlib import contextmanager
from contextvars import ContextVar

DEBUG_EMAIL_SESSION_KEY = "debug_email_destinations"
EMAIL_TEST_DESTINATIONS = {
    "delivered@resend.dev": ("Delivered", "Successful delivery"),
    "bounced@resend.dev": ("Bounced", "Recipient server rejects the email"),
    "complained@resend.dev": ("Spam complaint", "Recipient marks the email as spam"),
    "suppressed@resend.dev": ("Suppressed", "Resend suppresses delivery"),
}
DEFAULT_EMAIL_DESTINATIONS = ("delivered@resend.dev",)
_email_destinations = ContextVar(
    "debug_email_destinations", default=DEFAULT_EMAIL_DESTINATIONS
)


def normalize_debug_email_destinations(destinations):
    """Keep only known test addresses, with Delivered as the safe default."""
    if not isinstance(destinations, (list, tuple)):
        return list(DEFAULT_EMAIL_DESTINATIONS)
    return [
        address for address in EMAIL_TEST_DESTINATIONS if address in destinations
    ] or list(DEFAULT_EMAIL_DESTINATIONS)


def get_debug_email_destinations():
    """Return a copy of the validated destinations bound to the current context."""
    return list(_email_destinations.get())


def debug_email_summary(destinations):
    """Describe the selected outcomes for the toolbar."""
    return ", ".join(EMAIL_TEST_DESTINATIONS[address][0] for address in destinations)


def email_debug_context(destinations=None):
    """Use a queued selection, or inherit the current request's selection."""
    return override_debug_email_destinations(
        get_debug_email_destinations() if destinations is None else destinations
    )


@contextmanager
def override_debug_email_destinations(destinations):
    """Bind destinations to this request or job and restore the previous state."""
    token = _email_destinations.set(
        tuple(normalize_debug_email_destinations(destinations))
    )
    try:
        yield
    finally:
        _email_destinations.reset(token)
