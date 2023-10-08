from main.models import Notification


class NotificationMiddleware:
    """
    Middleware to attach unread notifications to every authenticated user's request object.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            unread_notifications = Notification.objects.filter(
                user=request.user, is_read=False
            )
            request.unread_notifications = unread_notifications

        response = self.get_response(request)
        return response
