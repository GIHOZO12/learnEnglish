from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, timedelta


class CustomUser(AbstractUser):
    """Custom User Model with extended profile features"""
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    profile_picture = models.ImageField(
        upload_to='users/profiles/', 
        null=True, 
        blank=True,
        help_text="User's profile picture"
    )
    bio = models.TextField(
        null=True, 
        blank=True, 
        max_length=500,
        help_text="User bio/description"
    )
    current_level = models.CharField(
        max_length=20, 
        choices=LEVEL_CHOICES, 
        default='beginner',
        help_text="Current English level"
    )
    total_xp = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        help_text="Total experience points"
    )
    current_streak = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        help_text="Current daily streak"
    )
    longest_streak = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        help_text="Longest daily streak achieved"
    )
    last_activity = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Last activity timestamp"
    )
    language_preference = models.CharField(
        max_length=10, 
        default='en',
        choices=[('en', 'English'), ('dari', 'Dari')],
        help_text="Preferred UI language"
    )
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Email verification status"
    )
    subscription_tier = models.CharField(
        max_length=20,
        default='free',
        choices=[('free', 'Free'), ('pro', 'Pro'), ('premium', 'Premium')],
        help_text="Subscription tier"
    )
    subscription_expires = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Subscription expiration date"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_customuser'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-total_xp']),
            models.Index(fields=['-current_streak']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.current_level})"
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def update_streak(self):
        """Check and update daily streak"""
        if self.last_activity:
            days_since = (timezone.now() - self.last_activity).days
            if days_since == 1:
                self.current_streak += 1
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
            elif days_since > 1:
                self.current_streak = 1
        else:
            self.current_streak = 1
        self.save()
    
    def add_xp(self, amount):
        """Add XP to user"""
        self.total_xp += amount
        self.save(update_fields=['total_xp'])
    
    def is_premium(self):
        """Check if user has active premium subscription"""
        if self.subscription_tier == 'free':
            return False
        if self.subscription_expires and self.subscription_expires < timezone.now():
            self.subscription_tier = 'free'
            self.save()
            return False
        return True
    
    def can_access_level(self, level):
        """Check if user can access a course level"""
        if level == 'beginner':
            return True
        elif level == 'intermediate' and self.current_level in ['intermediate', 'advanced']:
            return True
        elif level == 'advanced' and self.current_level == 'advanced':
            return True
        elif self.is_premium():
            return True
        return False
    
    def get_learning_progress(self):
        """Calculate overall learning progress percentage"""
        enrollments = self.course_enrollments.all()
        if not enrollments.exists():
            return 0
        
   
        total_progress = sum(enrollment.progress_percentage for enrollment in enrollments)
        return int(total_progress / enrollments.count()) if enrollments.count() > 0 else 0
    
    def get_completed_lessons(self):
        """Get total completed lessons"""
        return self.lesson_progress.filter(is_completed=True).count()
    
    def get_total_lessons(self):
        """Get total lessons in all enrolled courses"""
        from courses.models import Lesson
        course_ids = self.course_enrollments.values_list('course_id', flat=True)
        return Lesson.objects.filter(course_id__in=course_ids).count()
    
    def get_lessons_progress_percentage(self):
        """Get percentage of lessons completed"""
        total = self.get_total_lessons()
        if total == 0:
            return 0
        completed = self.get_completed_lessons()
        return int((completed / total) * 100)


class UserProfile(models.Model):
    """Extended user profile for additional data"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    total_lessons_completed = models.PositiveIntegerField(default=0)
    total_exercises_completed = models.PositiveIntegerField(default=0)
    total_posts = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    followers = models.ManyToManyField(CustomUser, related_name='following', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_userprofile'
    
    def __str__(self):
        return f"Profile: {self.user.username}"
    
    def get_follower_count(self):
        return self.followers.count()


class EmailVerification(models.Model):
    """Email verification tokens"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_emailverification'
    
    def is_valid(self):
        """Check if token is still valid (24 hours)"""
        return (datetime.now() - self.created_at).seconds < 86400
    
    def __str__(self):
        return f"Verification for {self.user.username}"
