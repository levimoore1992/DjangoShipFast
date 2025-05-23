from django.contrib import admin

from apps.payments.models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin for the Purchase model"""

    list_display = ("user", "purchasable_item", "created")
    search_fields = ("user__username",)
    readonly_fields = ("user", "purchasable_item", "status", "created")
