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
    template_name = "users/login.html"

    def form_invalid(self, form):
        form.add_error(None, "Invalid username or password.")
        return super().form_invalid(form)

    def get_success_url(self):
        # redirect the user to wherever you want after the successful register
        return resolve_url("home")


class RegisterView(TemplateView):
    template_name = "users/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Redirect to where you want the user to go after registering
            return redirect("home")
        else:
            return self.render_to_response({"form": form})


class LogoutView(BaseLogoutView):
    next_page = "home"


# Password reset views


class PasswordResetConfirmView(BasePasswordResetConfirmView):

    template_name = "users/password_reset/password_reset_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uidb64"] = self.kwargs["uidb64"]
        context["token"] = self.kwargs["token"]
        return context
