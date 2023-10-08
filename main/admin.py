from django.contrib import admin

from main.forms import NotificationAdminForm
from main.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user", "message")
    list_per_page = 25
