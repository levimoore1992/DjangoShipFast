from django import template
from django.core.cache import cache

from apps.main.consts import ContactStatus
from apps.main.models import SocialMediaLink

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


@register.inclusion_tag("components/social_media_row.html")
def social_media_row():
    """
    Grab social media links from the database and return them to the template.
    :return: A dictionary containing the social media links.
    """
    links = cache.get("social_media_links")
    if links is None:
        links = list(SocialMediaLink.objects.all())
        cache.set("social_media_links", links, 3600)
    return {"links": links}


@register.inclusion_tag("components/report_modal.html", takes_context=True)
def report_button(context, model_type, object_id):
    """
    Renders a report button with a modal for reporting.

    This is an inclusion tag that renders 'components/report_modal.html'.

    Args:
        context (dict): The template context.
        model_type (str): The type of the model to report.
        object_id (int): The ID of the object to report.

    Returns:
        dict: Context data for 'components/report_modal.html'.
    """
    request = context["request"]
    form = context.get("report_form")
    return {
        "model_type": model_type,
        "object_id": object_id,
        "report_form": form,
        "request": request,
    }
