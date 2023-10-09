from django.contrib import admin

from main.forms import NotificationAdminForm, TermsAndConditionsAdminForm
from main.models import Notification, TermsAndConditions


@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    """The Admin View for the TermsAndConditions Model."""

    list_display = ("created_at",)

    form = TermsAndConditionsAdminForm

    def get_readonly_fields(self, request, obj=None) -> tuple:
        """
        Return read-only fields based on user permissions.
        """
        readonly_fields = super().get_readonly_fields(request, obj)

        if (
            obj and not request.user.is_superuser
        ):  # If not a superuser and object exists
            return readonly_fields + ("terms",)
        return readonly_fields


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user", "message")
    list_per_page = 25
