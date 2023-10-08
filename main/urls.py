from django.urls import path


from .views import HomeView, MarkAsReadAndRedirectView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    # Notification views
    path(
        "mark_as_read_and_redirect/<int:notification_id>/<path:destination_url>/",
        MarkAsReadAndRedirectView.as_view(),
        name="mark_as_read_and_redirect",
    ),
]
