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
