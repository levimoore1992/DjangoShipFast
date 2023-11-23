import os

import requests
from debug_toolbar.panels import Panel
from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.static import serve

class ReplaceImagesPanel(Panel):

    title = "Replace Media Images"

    has_content = False

    @property
    def enabled(self):
        """Have the default option be switched off."""

        default = "off"
        # The user's cookies should override the default value
        return self.toolbar.request.COOKIES.get("djdt" + self.panel_id, default) == "on"


def save_local_media(path: str, content: bytes):
    """Save content to the local media directory."""

    full_path = os.path.join(settings.MEDIA_ROOT, path.strip("/"))

    # Make the directory if it does not exist yet.
    full_dir = os.path.dirname(full_path)
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)

    # Save the content.
    with open(full_path, "wb") as fh:
        fh.write(content)


def local_media_proxy(request, path, document_root=None, show_indexes=False):
    """Used to handle media files locally. Reads from the django tool bar cookies
    to see if the replace images flag is set. If so, after attempting to read
    the media locally, it will attempt to fetch the asset from production.
    This is purely a tool to help development, and save us from having to
    download media files.
    """
    # Double make sure that we are only doing this if you have debug == True.
    # This view should never be ran on production.
    if not settings.DEBUG:
        raise Http404

    # Check if the panel is ticked
    replace_images = False
    if "djdtReplaceImagesPanel" in request.COOKIES:
        replace_images = request.COOKIES["djdtReplaceImagesPanel"] == "on"

    # Try to return the locally served files first. The means that you can
    # still override the local state.
    try:
        return serve(request, path, document_root, show_indexes)

    # If the local file 404s, and we want to replace the image, request it
    # from production and pretend it is coming from here.
    except Http404 as e:
        # If we're not actually replacing images, raise the exemption now.
        if not replace_images:
            raise e

        url = (
            "your url here"
            + path.strip("/")
        )
        prod_response = requests.get(url)

        if prod_response.status_code == 200:

            # To save media locally, set SAVE_MEDIA to True in your local.py
            if getattr(settings, "SAVE_MEDIA", False):
                save_local_media(path, prod_response.content)

            # Return the response as if it was coming from us.
            return HttpResponse(
                prod_response.content, content_type=prod_response.headers["content-type"]
            )

        # If we couldn't successfully get the response from prod, then re-raise
        # the original 404 exception.
        raise e