from django.contrib.admin.utils import unquote
from django.views.generic import TemplateView, RedirectView
from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseRedirect,
    HttpResponse,
)

from main.models import Notification, TermsAndConditions


class HomeView(TemplateView):
    """View to the home page."""

    template_name = "main/home.html"


class TermsAndConditionsView(TemplateView):

    """View to the terms and conditions page."""

    template_name = "main/terms_and_conditions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["terms"] = TermsAndConditions.objects.latest("created_at").terms
        return context


class BadRequestView(TemplateView):
    """
    Handle 400 Bad Request errors.
    """

    template_name = "errors/400.html"

    def get(self, request, *args, **kwargs) -> HttpResponseBadRequest:
        response = super().get(request, *args, **kwargs)
        return HttpResponseBadRequest(response.rendered_content)


class ServerErrorView(TemplateView):
    """
    Handle 500 Internal Server Error.
    """

    template_name = "errors/500.html"

    def get(self, request, *args, **kwargs) -> HttpResponseServerError:
        response = super().get(request, *args, **kwargs)
        return HttpResponseServerError(response.rendered_content)


class MarkAsReadAndRedirectView(RedirectView):
    """
    A view that marks a given notification as read, then redirects to the notification's link.
    """

    permanent = False  # Make the redirect non-permanent

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """
        Handle GET requests.

        :param request: HttpRequest object
        :param notification_id: ID of the notification to mark as read
        :param destination_url: Encoded URL to redirect to after marking the notification as read
        :return: HttpResponse object
        """
        notification_id = kwargs.get("notification_id")
        destination_url = kwargs.get("destination_url")

        decoded_url = unquote(destination_url)  # Decode the URL

        # Its important the next line returns a 404 if it doesn't match because otherwise a malicious user could
        # use the redirect parameter to redirect any user to any site they want. Using our domain to gain credibility.
        try:
            notification = Notification.objects.get(
                id=notification_id, link=destination_url
            )
        except Notification.DoesNotExist:
            return HttpResponse(status=404)

        # Mark the notification as read
        notification.mark_as_read()

        return HttpResponseRedirect(decoded_url)  # Redirect to the decoded URL
