from django.contrib import admin
from .models import Subscription, UserSubscription, Payment, Invoice


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_monthly', 'price_yearly', 'course_access_level', 'is_active')
    list_filter = ('is_active', 'course_access_level')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date')
    search_fields = ('user__username',)
    readonly_fields = ('start_date',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'paid_at')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'payment', 'issued_at')
    search_fields = ('invoice_number',)
    readonly_fields = ('issued_at',)
