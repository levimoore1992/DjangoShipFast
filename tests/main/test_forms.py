from django.apps import apps
from django.test import TestCase
from django.contrib.auth.models import User
from apps.main.forms import ModelChoiceField, AuditLogConfigAdminForm


class ModelChoiceFieldTest(TestCase):
    """
    Test suite for the ModelChoiceField class.
    """

    def test_label_from_instance(self) -> None:
        """
        Test that label_from_instance method returns the correct label for a model instance.

        This method creates an instance of Django's built-in User model and a ModelChoiceField.
        It then tests whether the label_from_instance method correctly formats the label
        as 'app_label.model_name' for the given model instance.
        """
        user_instance: User = User()
        field: ModelChoiceField = ModelChoiceField(choices=[])
        label: str = field.label_from_instance(user_instance)

        expected_label: str = "auth.user"
        self.assertEqual(label, expected_label)


class AuditLogConfigAdminFormTest(TestCase):
    """
    Test suite for the AuditLogConfigAdminForm class.
    """

    def test_init(self) -> None:
        """
        Test the initialization of the AuditLogConfigAdminForm, particularly the model_name field choices.
        """
        form = AuditLogConfigAdminForm()
        expected_choices = AuditLogConfigAdminForm.get_model_choices()
        self.assertEqual(form.fields["model_name"].choices, expected_choices)

    def test_get_model_choices(self) -> None:
        """
        Test the get_model_choices static method.
        """
        choices = AuditLogConfigAdminForm.get_model_choices()
        models = apps.get_models()
        expected_choices = [
            (
                f"{model._meta.app_label}.{model._meta.model_name}",
                f"{model._meta.app_label}.{model._meta.model_name}",
            )
            for model in models
        ]
        self.assertEqual(choices, expected_choices)

    def test_clean_model_name(self) -> None:
        """
        Test the clean_model_name method of the form.
        """
        # Initialize the form to set up choices
        form = AuditLogConfigAdminForm()
        model_choice = form.fields["model_name"].choices[0][
            0
        ]  # Take the first available choice

        form_data = {"model_name": model_choice}
        form = AuditLogConfigAdminForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        cleaned_model_name = form.clean_model_name()
        self.assertEqual(cleaned_model_name, model_choice)
