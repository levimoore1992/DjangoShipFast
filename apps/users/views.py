from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.shortcuts import redirect, resolve_url
from django.views.generic import TemplateView

from django.contrib.auth.views import (
    LoginView as LoginViewBase,
    LogoutView as BaseLogoutView,
    PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from ipware import get_client_ip

from .forms import UserCreationForm
from .models import UserIP, UserDevice, User
from .utils import get_device_identifier


class LoginView(LoginViewBase):
    """Custom login view that uses the default login form."""

    template_name = "users/login.html"

    def form_invalid(self, form):
        """
        Overriding the default form_invalid method to add a custom error
        :param form:
        :return:
        """
        form.add_error(None, "Invalid username or password.")
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Overriding the default get_success_url method to redirect to the home page
        :return
        """
        # redirect the user to wherever you want after the successful register
        return resolve_url("home")


class RegisterView(TemplateView):
    """Custom register view that uses the UserCreationForm."""

    template_name = "users/register.html"

    def is_ip_or_device_blocked(self, request):
        """
        Checks if the IP or device is blocked or suspicious.

        Args:
        request (HttpRequest): The incoming request object.

        Returns:
        bool: True if the IP or device is blocked/suspicious, False otherwise.
        """
        ip_address, _ = get_client_ip(request)
        device_identifier = get_device_identifier(request)

        ip_blocked_or_suspicious = UserIP.objects.is_ip_blocked_or_suspicious(
            ip_address
        )
        device_blocked = UserDevice.objects.is_device_blocked(device_identifier)

        return ip_blocked_or_suspicious or device_blocked

    def get_context_data(self, **kwargs):
        """
        Overriding the default get_context_data method to add the form to the context
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        context["form"] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Overriding the default post method to handle the form submission
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            if self.is_ip_or_device_blocked(request):
                # Handle blocked/suspicious IP or device
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                messages.warning(
                    request,
                    "There was a problem with your account. Please email support if you believe its a mistake.",
                )
                return self.render_to_response({"form": form})
            user = form.save()
            user = authenticate(
                username=user.username,
                password=form.cleaned_data.get("password1"),
                backend="django.contrib.auth.backends.ModelBackend",
            )
            login(request, user)

            # Redirect to where you want the user to go after registering
            return redirect("home")
        return self.render_to_response({"form": form})


class LogoutView(BaseLogoutView):
    """
    Overriding the default logout view to redirect to the home page.

    Developer Notes:
        Although this doesn't really add logic that we couldn't do
         elsewhere it is done here to keep the logic in one place.
    """

    next_page = "home"


# Password reset views


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """

    template_name = "users/password_reset/password_reset_confirm.html"

    def get_context_data(self, **kwargs):
        """
        Overriding the default get_context_data method to add the uidb64 and token to the context
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        context["uidb64"] = self.kwargs["uidb64"]
        context["token"] = self.kwargs["token"]
        return context


def check_username(request):
    """
    Handles POST requests to check username availability, returning an HTML snippet.
    """
    username = request.POST.get("username", "")
    if User.objects.filter(username=username).exists():
        message = '<div class="text-red-500">That username is taken.</div>'
    else:
        message = '<div class="text-green-500">That username is available.</div>'
    return HttpResponse(message)
