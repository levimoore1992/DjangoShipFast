"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from apps.main.views import BadRequestView, ServerErrorView, ckeditor_upload

urlpatterns = [
    path("admin/", admin.site.urls),
    path("upload/", ckeditor_upload, name="ckeditor_upload"),
    path("accounts/", include("allauth.urls")),
    path("payments/", include("apps.payments.urls")),
    path("", include("apps.main.urls")),
]


# serve custom error views in production
if not settings.DEBUG:
    handler404 = BadRequestView.as_view()
    handler500 = ServerErrorView.as_view()

    import importlib

    debug_toolbar = importlib.import_module("debug_toolbar")
    dev_utils = importlib.import_module("core.dev_utils")

    local_media_proxy = getattr(dev_utils, "local_media_proxy")

    urlpatterns.append(
        path("__debug__/", include(debug_toolbar.urls)),
    )

    urlpatterns.extend(
        static(
            settings.MEDIA_URL,
            view=local_media_proxy,
            document_root=settings.MEDIA_ROOT,
        )
    )

    urlpatterns.append(
        path("hijack/", include("hijack.urls")),
    )
