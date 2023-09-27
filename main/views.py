import json
import stripe
from django.views.generic import TemplateView
from django.http import HttpResponseBadRequest, HttpResponseServerError, HttpResponse

from djstripe.models import Customer, PaymentMethod, PaymentIntent
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        has_card = False
        if user.is_authenticated:
            customer, created = Customer.get_or_create(subscriber=user)
            has_card = bool(customer.default_payment_method)
        context['has_card'] = has_card
        return context

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


@method_decorator([login_required, csrf_exempt], name='dispatch')
class CreatePaymentView(View):

    def post(self, request, *args, **kwargs) -> JsonResponse:
        data = json.loads(request.body)
        payment_method_id: str = data.get("payment_method_id")

        # Retrieve or create Dj-stripe Customer
        customer, created = Customer.get_or_create(subscriber=request.user)
        customer.api_retrieve()

        # Attach the payment method to Stripe customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer.id
        )

        # Manually sync PaymentMethod
        stripe_payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        PaymentMethod.sync_from_stripe_data(stripe_payment_method)

        try:
            # Get the Dj-stripe PaymentMethod
            djstripe_payment_method = PaymentMethod.objects.get(id=payment_method_id)
        except PaymentMethod.DoesNotExist:
            return JsonResponse({"error": "PaymentMethod does not exist"}, status=400)

        customer.default_payment_method = djstripe_payment_method
        customer.save()

        try:
            # Create a PaymentIntent with customer and payment method details
            payment_intent = stripe.PaymentIntent.create(
                amount=2000,  # in cents
                currency="usd",
                customer=customer.id,
                payment_method=payment_method_id,
                confirm=True  # Auto-confirm the payment
            )
        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)

        return JsonResponse({"status": payment_intent.status})


class StripeWebhookView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """
        Ensure this view is CSRF exempt.
        """
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle Stripe Webhooks for PaymentIntent.succeeded event.

        :param request: The HTTP request.
        :type request: HttpRequest
        :return: An HTTP response.
        :rtype: HttpResponse
        """
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        endpoint_secret = settings.DJSTRIPE_WEBHOOK_SECRET

        try:
            # Verify the webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # Handle the event
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            # Business logic here, e.g. mark an order as paid
            stripe_payment_intent = PaymentIntent.sync_from_stripe_data(payment_intent)

        return HttpResponse(status=200)