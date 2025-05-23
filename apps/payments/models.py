import stripe

from model_utils.models import TimeStampedModel
from django.db import models
from django.conf import settings

from apps.payments.consts import Plan

stripe.api_key = settings.STRIPE_API_SK


class Purchase(TimeStampedModel):
    """Represent a purchase of a plan by a user"""

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="purchases"
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=100)

    price_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The price that the user paid. This is stored on save to make sure it doesnt change even if we change the price",
    )

    is_active = models.BooleanField(default=False)

    class Meta:
        """
        Meta class for the model
        We set constraints so a user cant purchase the same plan twice
        """

        constraints = [
            models.UniqueConstraint(
                fields=["user", "plan"], name="unique_purchase_per_user_per_plan"
            )
        ]

    @property
    def status(self):
        """Return the status from Stripe"""
        if not self.payment_intent_id:
            return "No payment intent ID"

        try:
            payment_intent = stripe.PaymentIntent.retrieve(self.payment_intent_id)
            if (
                payment_intent.status == "requires_payment_method"
            ):  # Stripe returns this instead of failed when a payment fails
                return "Failed"

            return payment_intent.status
        except stripe.error.StripeError as e:
            # Handle potential Stripe API errors
            return f"Error retrieving status: {str(e)}"

    def activate(self):
        """Activate the purchase"""
        self.is_active = True
        self.save(update_fields=["is_active"])

    def deactivate(self):
        """Deactivate the purchase"""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def handle_dispute(self, stripe_event):
        """Handle a dispute event"""
        event_data = stripe_event["data"]["object"]

        # If we did not lose the dispute then do nothing
        if not event_data.get("status") == "lost":
            return

        self.deactivate()
