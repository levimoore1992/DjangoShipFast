from ipware import get_client_ip
from django.utils import timezone

from .models import UserIP, UserDevice

from .utils import get_device_identifier


class TrackUserIPAndDeviceMiddleware:
    """
    Middleware to track and record the IP address of authenticated users.

    Edge Cases:
    - This middleware only tracks authenticated users.
    - Users behind proxies or VPNs may have different or masked IPs.
    - Rapid IP changes (dynamic IPs) could lead to a large number of entries.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware.
        :param get_response:
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the incoming request.
        :param request:
        :return:
        """
        response = self.get_response(request)
        self.process_request(request)
        return response

    def process_request(self, request):
        """
        Extract and record the user's IP and device information.
        """
        if not request.user.is_authenticated:
            return
        client_ip, _ = get_client_ip(request)
        device_identifier = get_device_identifier(request)

        if client_ip:
            UserIP.objects.update_or_create(
                user=request.user,
                ip_address=client_ip,
                defaults={
                    "last_seen": timezone.now(),
                },
            )

        if device_identifier:
            UserDevice.objects.update_or_create(
                user=request.user,
                device_identifier=device_identifier,
                defaults={"last_seen": timezone.now()},
            )
