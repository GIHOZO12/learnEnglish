from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class Badge(models.Model):
    """Achievement badges"""
    
    BADGE_TYPES = [
        ('streak', 'Streak'),
        ('achievement', 'Achievement'),
        ('milestone', 'Milestone'),
        ('special', 'Special Event'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES, default='achievement')
    requirement = models.CharField(max_length=255, help_text="Requirement for earning badge")
    requirement_value = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gamification_badge'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """User earned badges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='users')
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gamification_userbadge'
        unique_together = ('user', 'badge')
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class Achievement(models.Model):
    """User achievements/milestones"""
    
    ACHIEVEMENT_TYPES = [
        ('first_lesson', 'First Lesson'),
        ('level_up', 'Level Up'),
        ('course_complete', 'Course Complete'),
        ('streak_milestone', 'Streak Milestone'),
        ('xp_milestone', 'XP Milestone'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=30, choices=ACHIEVEMENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    xp_earned = models.PositiveIntegerField(default=0)
    achieved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gamification_achievement'
        ordering = ['-achieved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Leaderboard(models.Model):
    """Weekly/monthly leaderboards"""
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    rank = models.PositiveIntegerField()
    xp = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    exercises_completed = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    
    class Meta:
        db_table = 'gamification_leaderboard'
        unique_together = ('user', 'period', 'start_date')
    
    def __str__(self):
        return f"{self.user.username} - {self.period} ({self.rank})"


class DailyChallenge(models.Model):
    """Daily learning challenges"""
    challenge_type = models.CharField(
        max_length=30,
        choices=[
            ('complete_lesson', 'Complete 1 Lesson'),
            ('complete_exercise', 'Complete 3 Exercises'),
            ('daily_streak', 'Keep Daily Streak'),
            ('community_post', 'Make Community Post'),
        ]
    )
    description = models.TextField()
    xp_reward = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gamification_dailychallenge'
    
    def __str__(self):
        return f"Challenge: {self.challenge_type}"


class UserDailyChallenge(models.Model):
    """Track user progress on daily challenges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_challenges')
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name='user_progress')
    progress = models.PositiveIntegerField(default=0)
    target = models.PositiveIntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    xp_earned = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'gamification_userdailychallenge'
        unique_together = ('user', 'challenge', 'date')
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.challenge_type} ({self.date})"


class Tier(models.Model):
    """User tiers based on XP"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    min_xp = models.PositiveIntegerField(unique=True)
    icon = models.ImageField(upload_to='tiers/', null=True, blank=True)
    perks = models.JSONField(default=dict, blank=True, help_text="Perks for this tier")
    
    class Meta:
        db_table = 'gamification_tier'
        ordering = ['min_xp']
    
    def __str__(self):
        return f"{self.name} ({self.min_xp} XP)"
    
    @classmethod
    def get_user_tier(cls, user):
        """Get user's current tier"""
        return cls.objects.filter(min_xp__lte=user.total_xp).last()
