from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, EmailVerification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('profile_picture', 'bio', 'current_level', 'language_preference')}),
        ('Gamification', {'fields': ('total_xp', 'current_streak', 'longest_streak', 'last_activity')}),
        ('Subscription', {'fields': ('subscription_tier', 'subscription_expires')}),
        ('Verification', {'fields': ('is_email_verified',)}),
    )
    list_display = ('username', 'email', 'current_level', 'total_xp', 'current_streak', 'subscription_tier')
    list_filter = ('current_level', 'subscription_tier', 'is_email_verified', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-total_xp',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_lessons_completed', 'total_exercises_completed', 'total_posts')
    search_fields = ('user__username',)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_valid')
    search_fields = ('user__username',)
