from django.urls import path


from .views import (
    HomeView,
    MarkAsReadAndRedirectView,
    TermsAndConditionsView,
    PrivacyPolicyView,
    ContactUsView,
    FAQListView,
    ReportView,
    robots_view,
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
    path("faqs/", FAQListView.as_view(), name="faqs"),
    path(
        "report/<str:model_name>/<int:object_id>/", ReportView.as_view(), name="report"
    ),
    # File path views
    path("robots.txt", robots_view, name="robots_view"),
    # Notification views
    path(
        "mark_as_read_and_redirect/<int:notification_id>/<path:destination_url>/",
        MarkAsReadAndRedirectView.as_view(),
        name="mark_as_read_and_redirect",
    ),
]
