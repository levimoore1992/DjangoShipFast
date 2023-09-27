from django.urls import path


from .views import HomeView, CreatePaymentView, StripeWebhookView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path('create_payment/', CreatePaymentView.as_view(), name='create_payment'),
    path("payments/webhook/", StripeWebhookView.as_view(), name="webhook"),

]
