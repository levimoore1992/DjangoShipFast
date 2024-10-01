from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from apps.users.models import User


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter to save the users with custom fields"""

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.email = user.email.lower()
        user.username = user.email  # Set username to email
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom Social Adapter to set username to email"""

    def pre_social_login(self, request, sociallogin):
        # This hook is called before the social account is logged in
        # and before the pre_social_login signal is emitted.
        user = sociallogin.user
        # If user exists, connect the account to the existing account and login
        if existing_user := User.objects.filter(email=user.email).first():
            sociallogin.connect(request, existing_user)

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.email = user.email.lower()
        user.username = user.email  # Set username to email
        return user
