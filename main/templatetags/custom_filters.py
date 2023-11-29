from django import template

from main.consts import ContactStatus

register = template.Library()


@register.filter(name="add_class")
def add_class(value, arg):
    """
    Adding a CSS class to a form field
    """
    return value.as_widget(attrs={"class": arg})


@register.filter(name="underscorize")
def underscorize(value: str) -> str:
    """
    Convert spaces in the given string to underscores.

    Args:
        value (str): The input string.

    Returns:
        str: The string with spaces replaced by underscores.
    """
    return value.replace(" ", "_")


@register.simple_tag
def contact_status_choices():
    """Return the choices for the contact status field."""
    return ContactStatus.choices()
