from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()


class Subscription(models.Model):
    """Subscription tiers"""
    
    TIER_TYPES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    ]
    
    name = models.CharField(max_length=100, unique=True, choices=TIER_TYPES)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_courses = models.PositiveIntegerField(default=-1, help_text="-1 for unlimited")
    course_access_level = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        default='beginner'
    )
    features = models.JSONField(default=list, blank=True, help_text="List of features")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'payments_subscription'
    
    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    """User active subscription"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='active_subscription')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('cancelled', 'Cancelled'), ('expired', 'Expired')],
        default='active'
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    stripe_customer_id = models.CharField(max_length=305, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'payments_usersubscription'
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription.name}"
    
    def is_active_subscription(self):
        return self.status == 'active' and self.end_date > datetime.now()
    
    def days_remaining(self):
        if self.is_active_subscription():
            return (self.end_date - datetime.now()).days
        return 0


class Payment(models.Model):
    """Payment transaction records"""
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('local', 'Local Payment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='stripe')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=255, unique=True, blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_payment'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment: {self.user.username} - ${self.amount} ({self.status})"
    
    def mark_completed(self):
        """Mark payment as completed"""
        self.status = 'completed'
        self.paid_at = datetime.now()
        self.save()


class Invoice(models.Model):
    """Invoice for payment"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=255, unique=True)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments_invoice'
    
    def __str__(self):
        return f"Invoice: {self.invoice_number}"
