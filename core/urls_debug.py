from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
import debug_toolbar

from .dev_utils import local_media_proxy


urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
]

urlpatterns += static(
    settings.MEDIA_URL,
    view=local_media_proxy,
    document_root=settings.MEDIA_ROOT,
)

urlpatterns.append(
    path("hijack/", include("hijack.urls")),
)
