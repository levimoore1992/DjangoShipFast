from ckeditor.widgets import CKEditorWidget
from django import forms

from main.models import Notification


class NotificationAdminForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = "__all__"
        widgets = {
            "message": CKEditorWidget(),
        }
