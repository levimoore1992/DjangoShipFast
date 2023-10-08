from django.contrib.admin.utils import unquote
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, RedirectView
from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseRedirect,
    HttpRequest,
    HttpResponse,
)

from main.models import Notification


class HomeView(TemplateView):
    template_name = "main/home.html"


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

    def get(
        self, request: HttpRequest, notification_id: int, destination_url: str
    ) -> HttpResponse:
        """
        Handle GET requests.

        :param request: HttpRequest object
        :param notification_id: ID of the notification to mark as read
        :param destination_url: Encoded URL to redirect to after marking the notification as read
        :return: HttpResponse object
        """
        decoded_url = unquote(destination_url)  # Decode the URL

        # Its important the next line returns a 404 if it doesn't match because otherwise a malicious user could
        # use the redirect parameter to redirect any user to any site they want. Using our domain to gain credibility.
        notification = get_object_or_404(
            Notification, id=notification_id, link=destination_url
        )

        # Mark the notification as read
        notification.mark_as_read()

        return HttpResponseRedirect(decoded_url)  # Redirect to the decoded URL
