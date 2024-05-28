from .forms import ReportForm


def report_form(request):
    """
    Adds the report form to the context of each template.

    Args:
        request: The HttpRequest object.

    Returns:
        dict: A dictionary with the report form instance.
    """
    return {"report_form": ReportForm()}


def notifications(request):
    """A context processor that provides the user's notifications to all templates."""
    if request.user.is_authenticated:
        return {"notifications": request.user.notifications.filter(is_read=False)}
    return {}
