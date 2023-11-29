from django.urls import path


from .views import (
    HomeView,
    MarkAsReadAndRedirectView,
    TermsAndConditionsView,
    PrivacyPolicyView,
    ContactUsView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path(
        "terms-and-conditions/",
        TermsAndConditionsView.as_view(),
        name="terms_and_conditions",
    ),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("contact-us/", ContactUsView.as_view(), name="contact_us"),
    # Notification views
    path(
        "mark_as_read_and_redirect/<int:notification_id>/<path:destination_url>/",
        MarkAsReadAndRedirectView.as_view(),
        name="mark_as_read_and_redirect",
    ),
]
