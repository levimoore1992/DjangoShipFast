"""Development-only form and endpoint for Resend test destinations."""

from debug_toolbar.decorators import require_show_toolbar
from django import forms
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from core.debug.email import (
    DEBUG_EMAIL_SESSION_KEY,
    EMAIL_TEST_DESTINATIONS,
    normalize_debug_email_destinations,
)


class EmailDestinationsForm(forms.Form):
    """Require one or more of Resend's official simulation destinations."""

    destinations = forms.MultipleChoiceField(
        choices=[
            (address, label) for address, (label, _) in EMAIL_TEST_DESTINATIONS.items()
        ],
        error_messages={
            "required": "Select at least one test outcome.",
            "invalid_choice": "Choose only the listed Resend test destinations.",
        },
    )


def email_destinations_context(request, destinations, return_url):
    """Build the shared checkbox form for the panel and validation page."""
    return {
        "choices": [
            {
                "address": address,
                "label": label,
                "description": description,
                "selected": address in destinations,
            }
            for address, (label, description) in EMAIL_TEST_DESTINATIONS.items()
        ],
        "save_url": reverse("djdt:email_destinations"),
        "csrf_token": get_token(request),
        "return_url": return_url,
    }


@require_show_toolbar
@require_POST
@csrf_protect
def update_email_destinations(request):
    """Save a validated selection in the current browser's session."""
    if not settings.DEBUG:
        raise Http404
    return_url = request.POST.get("next", "/")
    if not url_has_allowed_host_and_scheme(
        return_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return_url = "/"
    form = EmailDestinationsForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "debug_toolbar/email_destinations_error.html",
            {
                **email_destinations_context(
                    request, request.POST.getlist("destinations"), return_url
                ),
                "error": form.errors["destinations"][0],
            },
            status=400,
        )
    destinations = normalize_debug_email_destinations(form.cleaned_data["destinations"])
    request.session[DEBUG_EMAIL_SESSION_KEY] = destinations
    return HttpResponseRedirect(return_url)
