from django.contrib.auth import login
from django.shortcuts import redirect, resolve_url
from django.views.generic import TemplateView

from django.contrib.auth.views import (
    LoginView as LoginViewBase,
    LogoutView as BaseLogoutView,
    PasswordResetConfirmView as BasePasswordResetConfirmView,
)

from users.forms import UserCreationForm


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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
