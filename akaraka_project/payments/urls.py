from django.urls import path
from .views import (
    SubscriptionPlansView, CheckoutView, PaymentHistoryView,
    InvoiceView, CancelSubscriptionView
)

app_name = 'payments'

urlpatterns = [
    path('plans/', SubscriptionPlansView.as_view(), name='plans'),
    path('checkout/<int:subscription_id>/', CheckoutView.as_view(), name='checkout'),
    path('history/', PaymentHistoryView.as_view(), name='history'),
    path('invoice/<int:payment_id>/', InvoiceView.as_view(), name='invoice'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel'),
]
