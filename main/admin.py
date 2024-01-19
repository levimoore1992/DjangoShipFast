from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils import timezone

from main.consts import ContactStatus
from main.forms import (
    NotificationAdminForm,
    TermsAndConditionsAdminForm,
    PrivacyPolicyAdminForm,
    ContactAdminForm,
    AuditLogConfigAdminForm,
)
from main.models import (
    Notification,
    TermsAndConditions,
    PrivacyPolicy,
    Contact,
    AuditLogConfig,
)


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    """
    Admin for the PrivacyPolicy Model.
    """

    list_display = ("created_at",)
    form = PrivacyPolicyAdminForm


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
    """
    The Admin View for the Notification Model.
    """

    form = NotificationAdminForm
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user", "message")
    list_per_page = 25


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    The Admin View for the Contact Model.

    This is where the admin can change the status of the contact request.
    """

    form = ContactAdminForm

    list_display = ("name", "email", "subject", "contact_date", "status", "type")
    list_filter = ("status", "type")
    readonly_fields = (
        "name",
        "email",
        "subject",
        "message",
        "contact_date",
        "type",
        "resolved_date",
        "status",
    )

    def response_change(self, request, obj):
        """
        Handle custom actions when the change form is submitted.
        """
        for status in ContactStatus:
            status_key = f"_{status.value.lower().replace(' ', '_')}"
            if status_key in request.POST:
                obj.status = status.value
                if status == ContactStatus.RESOLVED:  # If the status is 'RESOLVED'
                    obj.resolved_date = timezone.now()  # Set the resolved_date
                elif (
                    status != ContactStatus.RESOLVED and obj.resolved_date
                ):  # If the status is not 'RESOLVED' and resolved_date is set
                    obj.resolved_date = None  # Reset the resolved_date
                obj.save()
                messages.success(request, f"Contact request marked as {status.value}.")
                return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)


@admin.register(AuditLogConfig)
class AuditLogConfigAdmin(admin.ModelAdmin):
    """
    The Admin View for the AuditLogConfig Model.
    """

    form = AuditLogConfigAdminForm
    list_display = ["model_name"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.register_model()

    def delete_model(self, request, obj):
        obj.unregister_model()
        super().delete_model(request, obj)
