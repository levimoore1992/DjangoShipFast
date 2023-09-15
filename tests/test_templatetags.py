from django import forms
from django.template import Context, Template

from tests.base import BaseTestCase


class AddClassTemplateTagTest(BaseTestCase):
    """Test cases for the 'add_class' template tag."""

    def setUp(self) -> None:
        """Setup the initial data for the tests."""
        super().setUp()

        # Dummy form for testing
        class TestForm(forms.Form):
            """Dummy form for testing."""

            test_field = forms.CharField()

        self.form = TestForm()

    def test_add_class_template_tag(self) -> None:
        """Test the 'add_class' template tag."""
        # Load the template
        template_content = """
        {% load custom_filters %}
        {{ form.test_field|add_class:"desired-css-class" }}
        """
        template = Template(template_content)

        # Render the template
        rendered_template = template.render(Context({"form": self.form}))

        # Check if the class is added to the widget
        self.assertIn('class="desired-css-class"', rendered_template)
