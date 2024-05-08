"""
URL configuration for django_template project.

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

from apps.main.views import BadRequestView, ServerErrorView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("apps.users.urls")),
    path("", include("apps.main.urls")),
]


# serve custom error views in production
if not settings.DEBUG:
    handler404 = BadRequestView.as_view()
    handler500 = ServerErrorView.as_view()

if settings.DEBUG:
    import debug_toolbar
    from .dev_utils import local_media_proxy

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
