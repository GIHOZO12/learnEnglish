from django.contrib import admin
from .models import Certificate, CertificateTemplate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'user', 'course', 'issue_date', 'is_verified')
    list_filter = ('is_verified', 'issue_date')
    search_fields = ('user__username', 'course__title', 'certificate_number')
    readonly_fields = ('issue_date', 'certificate_number', 'verification_code')


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
