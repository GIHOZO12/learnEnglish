from django.urls import path
from .views import (
    BadgesView, AchievementsView, GlobalLeaderboardView,
    WeeklyLeaderboardView, DailyChallengeView, UserTierView
)

app_name = 'gamification'

urlpatterns = [
    path('badges/', BadgesView.as_view(), name='badges'),
    path('achievements/', AchievementsView.as_view(), name='achievements'),
    path('leaderboard/', GlobalLeaderboardView.as_view(), name='leaderboard'),
    path('leaderboard/weekly/', WeeklyLeaderboardView.as_view(), name='weekly_leaderboard'),
    path('challenges/', DailyChallengeView.as_view(), name='daily_challenge'),
    path('tier/', UserTierView.as_view(), name='user_tier'),
]
