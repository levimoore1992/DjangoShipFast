from django.views.generic import TemplateView
from django.http import HttpResponseBadRequest, HttpResponseServerError


class HomeView(TemplateView):
    template_name = "main/home.html"


class BadRequestView(TemplateView):
    """
    Handle 400 Bad Request errors.
    """

    template_name = "errors/400.html"

    def get(self, request, *args, **kwargs) -> HttpResponseBadRequest:
        response = super().get(request, *args, **kwargs)
        return HttpResponseBadRequest(response.rendered_content)


class ServerErrorView(TemplateView):
    """
    Handle 500 Internal Server Error.
    """

    template_name = "errors/500.html"

    def get(self, request, *args, **kwargs) -> HttpResponseServerError:
        response = super().get(request, *args, **kwargs)
        return HttpResponseServerError(response.rendered_content)
