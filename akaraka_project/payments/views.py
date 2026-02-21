from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
import stripe
from .models import Subscription, Payment, UserSubscription
from datetime import datetime, timedelta

stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionPlansView(View):
    """Browse subscription plans"""
    def get(self, request):
        plans = Subscription.objects.filter(is_active=True)
        context = {
            'plans': plans,
            'user_subscription': None,
        }
        
        if request.user.is_authenticated:
            context['user_subscription'] = getattr(request.user, 'active_subscription', None)
        
        return render(request, 'payments/subscription_plans.html', context)


class CheckoutView(LoginRequiredMixin, View):
    """Stripe checkout"""
    def get(self, request, subscription_id):
        subscription = get_object_or_404(Subscription, id=subscription_id, is_active=True)
        
        # Check if user already has this subscription
        if request.user.active_subscription and request.user.active_subscription.subscription == subscription:
            messages.info(request, f'You already have {subscription.name} subscription.')
            return redirect('payments:plans')
        
        context = {
            'subscription': subscription,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, 'payments/checkout.html', context)
    
    def post(self, request, subscription_id):
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        try:
            # Create Stripe Customer
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name(),
            )
            
            # Create charge
            charge = stripe.Charge.create(
                amount=int(subscription.price_monthly * 100),  # Convert to cents
                currency='usd',
                customer=customer.id,
                source=request.POST.get('stripeToken'),
                description=f'{subscription.name} Subscription - {request.user.email}',
            )
            
            # Record payment
            payment = Payment.objects.create(
                user=request.user,
                subscription=subscription,
                amount=subscription.price_monthly,
                currency='USD',
                payment_method='stripe',
                status='completed',
                transaction_id=charge.id,
                stripe_charge_id=charge.id,
                paid_at=datetime.now(),
            )
            
            # Create/update subscription
            end_date = datetime.now() + timedelta(days=30)
            user_subscription, created = UserSubscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'subscription': subscription,
                    'end_date': end_date,
                    'stripe_customer_id': customer.id,
                }
            )
            
            if not created:
                user_subscription.subscription = subscription
                user_subscription.end_date = end_date
                user_subscription.stripe_customer_id = customer.id
                user_subscription.status = 'active'
                user_subscription.save()
            
            # Update user tier
            request.user.subscription_tier = subscription.name
            request.user.subscription_expires = end_date
            request.user.save()
            
            messages.success(request, f'Welcome to {subscription.name}! Your subscription is active.')
            return redirect('courses:dashboard')
        
        except stripe.error.CardError as e:
            messages.error(request, f'Payment failed: {e.user_message}')
            return redirect('payments:checkout', subscription_id=subscription.id)


class PaymentHistoryView(LoginRequiredMixin, ListView):
    """User payment history"""
    model = Payment
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')


class InvoiceView(LoginRequiredMixin, View):
    """Download invoice"""
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        if hasattr(payment, 'invoice') and payment.invoice.pdf_file:
            return redirect(payment.invoice.pdf_file.url)
        
        messages.error(request, 'Invoice not available.')
        return redirect('payments:history')


class CancelSubscriptionView(LoginRequiredMixin, View):
    """Cancel subscription"""
    def post(self, request):
        try:
            user_subscription = request.user.active_subscription
            
            # Cancel with Stripe
            if user_subscription.stripe_subscription_id:
                stripe.Subscription.delete(user_subscription.stripe_subscription_id)
            
            # Mark as cancelled
            user_subscription.status = 'cancelled'
            user_subscription.save()
            
            # Revert user tier
            request.user.subscription_tier = 'free'
            request.user.subscription_expires = None
            request.user.save()
            
            messages.success(request, 'Subscription cancelled. You can resubscribe anytime.')
            return redirect('payments:plans')
        
        except Exception as e:
            messages.error(request, f'Error cancelling subscription: {str(e)}')
            return redirect('payments:history')
