python manage.py migrate
python manage.py shell << END
from django.contrib.auth import get_user_model
from payments.models import Subscription
from gamification.models import Badge, Tier

User = get_user_model()

# Create default subscriptions
Subscription.objects.get_or_create(
    name='free',
    defaults={
        'description': 'Free tier with beginner courses',
        'price_monthly': 0,
        'course_access_level': 'beginner',
        'max_courses': -1,
        'features': ['Beginner courses', 'Daily exercises', 'Community access', 'Badges & streaks']
    }
)

Subscription.objects.get_or_create(
    name='pro',
    defaults={
        'description': 'Pro tier with intermediate courses',
        'price_monthly': 9.99,
        'course_access_level': 'intermediate',
        'max_courses': -1,
        'features': ['All Free features', 'Intermediate courses', 'Certificates', 'Ad-free', 'Priority support']
    }
)

Subscription.objects.get_or_create(
    name='premium',
    defaults={
        'description': 'Premium tier with all courses',
        'price_monthly': 19.99,
        'course_access_level': 'advanced',
        'max_courses': -1,
        'features': ['All Pro features', 'Advanced courses', '1-on-1 tutoring', 'Offline downloads', 'Career guidance']
    }
)

# Create default badges
Badge.objects.get_or_create(
    name='First Lesson',
    defaults={
        'description': 'Complete your first lesson',
        'badge_type': 'achievement',
        'requirement': 'complete_lesson',
        'requirement_value': 1,
        'xp_reward': 5
    }
)

Badge.objects.get_or_create(
    name='Week Warrior',
    defaults={
        'description': 'Maintain a 7-day streak',
        'badge_type': 'streak',
        'requirement': 'daily_streak',
        'requirement_value': 7,
        'xp_reward': 50
    }
)

# Create user tiers
Tier.objects.get_or_create(
    name='Beginner',
    defaults={
        'min_xp': 0,
        'perks': {'special_badge': 'Beginner Badge'}
    }
)

Tier.objects.get_or_create(
    name='Intermediate',
    defaults={
        'min_xp': 500,
        'perks': {'special_badge': 'Intermediate Badge', 'unlock_content': True}
    }
)

Tier.objects.get_or_create(
    name='Advanced',
    defaults={
        'min_xp': 1500,
        'perks': {'special_badge': 'Advanced Badge', 'unlock_all_content': True}
    }
)

print('✓ Initial data loaded successfully!')
END
