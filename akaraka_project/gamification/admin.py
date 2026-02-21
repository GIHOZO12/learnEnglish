from django.contrib import admin
from .models import Badge, UserBadge, Achievement, Leaderboard, DailyChallenge, UserDailyChallenge, Tier


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'requirement', 'xp_reward', 'is_active')
    list_filter = ('badge_type', 'is_active')
    search_fields = ('name', 'description')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('earned_at',)
    search_fields = ('user__username', 'badge__name')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'achievement_type', 'xp_earned', 'achieved_at')
    list_filter = ('achievement_type', 'achieved_at')
    search_fields = ('user__username', 'title')


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'period', 'rank', 'xp', 'lessons_completed', 'exercises_completed')
    list_filter = ('period', 'start_date')
    search_fields = ('user__username',)


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('challenge_type', 'xp_reward', 'is_active')
    list_filter = ('challenge_type', 'is_active')


@admin.register(UserDailyChallenge)
class UserDailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'date', 'progress', 'target', 'is_completed')
    list_filter = ('is_completed', 'date', 'challenge__challenge_type')
    search_fields = ('user__username',)


@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_xp', 'description')
    list_filter = ('min_xp',)
    search_fields = ('name',)
