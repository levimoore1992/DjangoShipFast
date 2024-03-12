from ckeditor.widgets import CKEditorWidget
from django import forms
from django.apps import apps
from django.core.validators import MinLengthValidator, EmailValidator
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


from .consts import ContactType, ContactStatus
from .models import (
    Notification,
    TermsAndConditions,
    PrivacyPolicy,
    Contact,
    AuditLogConfig,
    FAQ,
)


class NotificationAdminForm(forms.ModelForm):
    """
    The form for the Notification Model specifically in the admin.
    """

    link = forms.URLField(assume_scheme="https")

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


class ContactForm(forms.ModelForm):
    """
    Form for user's contact request based on the Contact model.
    """

    name = forms.CharField(
        max_length=255,
        validators=[MinLengthValidator(2)],
        help_text="Your full name.",
        label="Full Name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        validators=[EmailValidator()],
        help_text="The email address where we can contact you.",
        label="Email Address",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    type = forms.ChoiceField(
        choices=ContactType.choices(),
        help_text="Type of your request.",
        label="Contact Type",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    subject = forms.CharField(
        max_length=255,
        help_text="The main topic or reason for contacting us.",
        label="Subject",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5, "cols": 50})
    )
    # next line we set label as empty string so it doesn't show up in the form
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible, label="")

    class Meta:
        model = Contact
        fields = [
            "name",
            "email",
            "type",
            "subject",
            "message",
            "captcha",
        ]


class ContactAdminForm(forms.ModelForm):
    """The form for the Contact Us model specifically in the admin."""

    status = forms.ChoiceField(choices=ContactStatus.choices())

    class Meta:
        model = Contact
        fields = "__all__"


class ModelChoiceField(forms.ChoiceField):
    """
    The model choice field for the AuditLogConfigAdminForm.
    """

    def label_from_instance(self, obj):
        """
        Return the label for the option.
        :param obj:
        :return:
        """
        return f"{obj._meta.app_label}.{obj._meta.model_name}"


class AuditLogConfigAdminForm(forms.ModelForm):
    """
    The form for the AuditLogConfig Model specifically in the admin.
    """

    model_name = ModelChoiceField()

    def __init__(self, *args, **kwargs):
        """
        Initialize the form.
        We get the choices from the get_model_choices method.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.fields["model_name"].choices = self.get_model_choices()

    @staticmethod
    def get_model_choices():
        """
        This function returns the choices for the model_name field.
        It is intended for the AuditLogConfigAdminForm to generate all the model choices
        """
        models = apps.get_models()
        choices = [
            (
                f"{model._meta.app_label}.{model._meta.model_name}",
                f"{model._meta.app_label}.{model._meta.model_name}",
            )
            for model in models
        ]
        return choices

    class Meta:
        model = AuditLogConfig
        fields = ["model_name"]

    def clean_model_name(self):
        """
        Clean the model name field.
        :return:
        """
        model_label = self.cleaned_data["model_name"]
        return model_label


class FAQForm(forms.ModelForm):
    """
    Form for the FAQ model.
    """

    class Meta:
        model = FAQ
        fields = "__all__"
        widgets = {
            "question": CKEditorWidget(),
            "answer": CKEditorWidget(),
        }


class ReportForm(forms.Form):
    """
    Form for submitting a report about inappropriate content.

    Attributes:
        reason (CharField): A textarea input for the report reason.
    """

    reason = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}), required=True
    )
