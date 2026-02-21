# Akaraka - English-Dari Learning Platform

Complete MVP implementation of a Duolingo-inspired learning platform.

## Project Setup

### Requirements
- Python 3.9+
- PostgreSQL 12+
- Django 4.2
- Django Templates + Tailwind CSS

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "SECRET_KEY=your-secret-key-here" > .env
echo "DEBUG=True" >> .env
echo "DB_NAME=akaraka_db" >> .env
echo "DB_USER=postgres" >> .env
echo "DB_PASSWORD=password" >> .env
echo "STRIPE_PUBLIC_KEY=pk_test_xxx" >> .env
echo "STRIPE_SECRET_KEY=sk_test_xxx" >> .env

# Migrate database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

## Apps Structure

### 1. **Users** (`users/`)
- Custom user model with XP, streaks, level tracking
- Authentication (register, login, logout)
- User profiles and leaderboards
- Email verification support

**Models:**
- `CustomUser`: Custom user with gamification fields
- `UserProfile`: Extended profile data
- `EmailVerification`: Email verification tokens

### 2. **Courses** (`courses/`)
- Course management (beginner/intermediate/advanced)
- Lessons with English + Dari content
- Vocabulary with pronunciation
- Progress tracking

**Models:**
- `Course`: Main course object
- `Lesson`: Individual lessons
- `Vocabulary`: Words with Dari translations
- `LessonProgress`: User progress tracking
- `CourseEnrollment`: Enrollment management

### 3. **Exercises** (`exercises/`)
- MCQ (Multiple Choice Questions)
- Matching exercises
- Typing exercises
- Listening comprehension

**Models:**
- `Exercise`: Base exercise model
- `MCQQuestion`, `MCQOption`: MCQ data
- `MatchingExercise`, `MatchingPair`: Matching data
- `TypingExercise`, `TypingPrompt`: Typing data
- `ListeningExercise`, `ListeningQuestion`: Listening data
- `UserExerciseResponse`: Response grading and tracking

### 4. **Gamification** (`gamification/`)
- Badges and achievements
- XP system
- Daily streaks
- Leaderboards
- User tiers

**Models:**
- `Badge`: Achievement badges
- `UserBadge`: Earned badges
- `Achievement`: User milestones
- `Leaderboard`: Rankings
- `DailyChallenge`: Daily tasks
- `Tier`: User levels by XP

### 5. **Community** (`community/`)
- Posts and discussions
- Comments with nesting
- User testimonials
- Content moderation

**Models:**
- `Post`: Forum posts
- `Comment`: Post comments
- `Testimony`: Learning testimonies
- `Report`: Content reports
- `CommunityModerator`: Moderator roles

### 6. **Payments** (`payments/`)
- Subscription tiers (Free, Pro, Premium)
- Stripe integration
- Payment tracking
- Invoice generation

**Models:**
- `Subscription`: Subscription plans
- `UserSubscription`: Active subscriptions
- `Payment`: Payment records
- `Invoice`: Invoice tracking

### 7. **Certificates** (`certificates/`)
- Certificate generation on course completion
- PDF export
- Certificate verification
- Templates

**Models:**
- `Certificate`: Earned certificates
- `CertificateTemplate`: Certificate designs

## Key Features

### ✅ Authentication
- Custom user model with email/username login
- Social auth ready (Django-allauth compatible)
- Email verification support

### ✅ Courses
- Beginner/Intermediate/Advanced levels
- English + Dari bilingual content
- Audio pronunciation files
- Progress tracking

### ✅ Exercises
- MCQ with instant grading
- Matching exercises
- Typing exercises with spell-checking
- Listening comprehension
- Automatic XP calculation

### ✅ Gamification
- XP system with configurable rewards
- Daily streaks (tracked automatically)
- Badges for milestones
- Global + weekly leaderboards
- User tiers

### ✅ Community
- Forum with tagging
- Nested comments
- Post moderation
- User testimonials
- Content reporting

### ✅ Payments
- Stripe integration
- Monthly subscriptions
- Tier-based access control
- Payment history
- Invoice tracking

### ✅ Certificates
- Auto-generation on course completion
- PDF download
- Certificate verification system
- Customizable templates

## Admin Panel Features

All models have fully configured Django admin interfaces:
```
/admin/
```

Manage:
- Users and profiles
- Courses and lessons
- Exercises and responses
- Badges and achievements
- Community posts and moderation
- Payments and subscriptions
- Certificates

## Frontend Stack

- **Templates:** Django Templates
- **CSS:** Tailwind CSS (CDN)
- **Icons:** Unicode Emojis + Tailwind
- **JavaScript:** Vanilla JS (for interactivity)

## Database Schema

PostgreSQL with optimized indexes:
- Composite unique constraints for user progress
- Full-text search on posts
- JSON fields for flexible data (exercises, perks)

## Security Features

- CSRF protection
- XSS prevention
- SQL injection prevention (Django ORM)
- Secure password hashing
- Email verification
- Payment PCI compliance (Stripe)

## Performance Optimizations

- Database query optimization (select_related, prefetch_related)
- Caching for leaderboards
- Lazy loading of exercise responses
- Optimized image handling
- Low-bandwidth friendly

## Next Steps

1. Load initial data:
```bash
python manage.py loaddata initial_data.json
```

2. Create admin user for course management

3. Upload course content (lessons, audio, images)

4. Configure Stripe keys for production

5. Set up email backend (Gmail/SendGrid)

6. Deploy to production server

---

**Built with ❤️ for English learners**
