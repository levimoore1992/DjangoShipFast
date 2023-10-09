from ckeditor.widgets import CKEditorWidget
from django import forms

from main.models import Notification, TermsAndConditions


class NotificationAdminForm(forms.ModelForm):
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
