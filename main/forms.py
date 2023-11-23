from ckeditor.widgets import CKEditorWidget
from django import forms

from .models import Notification, TermsAndConditions, PrivacyPolicy


class NotificationAdminForm(forms.ModelForm):
    """
    The form for the Notification Model specifically in the admin.
    """

    class Meta:
        model = Notification
        fields = "__all__"
        widgets = {
            "message": CKEditorWidget(),
        }


class TermsAndConditionsAdminForm(forms.ModelForm):
    """The form for the TermsAndConditions Model specifically in the admin."""

    class Meta:
        model = TermsAndConditions
        fields = ["terms"]
        widgets = {
            "terms": CKEditorWidget,
        }


class PrivacyPolicyAdminForm(forms.ModelForm):
    """The form for the PrivacyPolicy Model specifically in the admin."""

    class Meta:
        model = PrivacyPolicy
        fields = ["policy"]
        widgets = {
            "policy": CKEditorWidget,
        }
