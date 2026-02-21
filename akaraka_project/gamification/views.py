from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Badge, Achievement, Leaderboard, DailyChallenge, UserDailyChallenge, Tier
from users.models import CustomUser


class BadgesView(LoginRequiredMixin, ListView):
    """User's badges/achievements"""
    model = Badge
    template_name = 'gamification/badges.html'
    context_object_name = 'badges'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        earned_badges = user.earned_badges.values_list('badge_id', flat=True)
        context['earned_badge_ids'] = list(earned_badges)
        return context


class AchievementsView(LoginRequiredMixin, ListView):
    """User's achievements"""
    model = Achievement
    template_name = 'gamification/achievements.html'
    context_object_name = 'achievements'
    paginate_by = 20
    
    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user).order_by('-achieved_at')


class GlobalLeaderboardView(ListView):
    """Global XP leaderboard"""
    model = CustomUser
    template_name = 'gamification/leaderboard.html'
    context_object_name = 'users'
    paginate_by = 50
    
    def get_queryset(self):
        return CustomUser.objects.filter(is_active=True).order_by('-total_xp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            rank = list(CustomUser.objects.filter(
                is_active=True,
                total_xp__gt=self.request.user.total_xp
            ).values_list('id', flat=True)).count() + 1
            context['user_rank'] = rank
            context['period'] = 'All Time'
        return context


class WeeklyLeaderboardView(ListView):
    """Weekly XP leaderboard"""
    model = Leaderboard
    template_name = 'gamification/weekly_leaderboard.html'
    context_object_name = 'entries'
    paginate_by = 50
    
    def get_queryset(self):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        return Leaderboard.objects.filter(
            period='weekly',
            start_date=week_start
        ).select_related('user').order_by('rank')


class DailyChallengeView(LoginRequiredMixin, View):
    """Daily challenges"""
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        
        # Get today's challenges
        challenges = DailyChallenge.objects.filter(is_active=True)
        user_challenges = []
        
        for challenge in challenges:
            user_challenge, created = UserDailyChallenge.objects.get_or_create(
                user=user,
                challenge=challenge,
                date=today
            )
            user_challenges.append(user_challenge)
        
        context = {
            'user_challenges': user_challenges,
            'total_daily_xp': sum(uc.xp_earned for uc in user_challenges),
        }
        return render(request, 'gamification/daily_challenge.html', context)


class UserTierView(LoginRequiredMixin, View):
    """User tier/level page"""
    def get(self, request):
        user = request.user
        current_tier = Tier.get_user_tier(user)
        
        # Get next tier
        all_tiers = Tier.objects.all()
        next_tier = None
        xp_to_next = 0
        
        if current_tier:
            next_tier = all_tiers.filter(min_xp__gt=current_tier.min_xp).first()
            if next_tier:
                xp_to_next = next_tier.min_xp - user.total_xp
        else:
            next_tier = all_tiers.first()
            if next_tier:
                xp_to_next = next_tier.min_xp - user.total_xp
        
        context = {
            'current_tier': current_tier,
            'next_tier': next_tier,
            'xp_to_next': max(xp_to_next, 0),
            'all_tiers': all_tiers,
            'earned_badges': user.earned_badges.all(),
            'achievements': user.achievements.all()[:10],
        }
        return render(request, 'gamification/user_tier.html', context)
