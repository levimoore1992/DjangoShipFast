from django.contrib import messages
from django.contrib.admin.utils import unquote
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, RedirectView
from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseRedirect,
    HttpResponse,
)

from main.forms import ContactForm
from main.models import Notification, TermsAndConditions, PrivacyPolicy


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


class PrivacyPolicyView(TemplateView):

    """View to the privacy policy page."""

    template_name = "main/privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["privacy_policy"] = PrivacyPolicy.objects.latest("created_at")
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


class ContactUsView(View):
    """
    View to handle the Contact Us form.
    """

    template_name = "main/contact_us.html"

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests. Display the contact form.
        """
        form = ContactForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests. Process the form submission.
        """
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, "Your message has been sent.")
            return redirect("home")
        return render(request, self.template_name, {"form": form})
