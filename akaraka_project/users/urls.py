from django.urls import path
from .views import (
    HomeView, RegisterView, LoginView, LogoutView,
    ProfileDetailView, ProfileUpdateView, LeaderboardView, StreakLeaderboardView
)

app_name = 'users'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/<str:username>/', ProfileDetailView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('leaderboard/streaks/', StreakLeaderboardView.as_view(), name='streak_leaderboard'),
]
