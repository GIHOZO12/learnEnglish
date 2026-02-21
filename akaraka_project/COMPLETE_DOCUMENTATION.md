# 🌍 AKARAKA - Complete Platform Documentation

## Overview

**Akaraka** is a full-featured English-Dari learning platform inspired by Duolingo and British Council standards. It's built with Django, PostgreSQL, and Django Templates + Tailwind CSS.

---

## 🚀 Quick Start

### Installation (Windows)

```powershell
# Navigate to project
cd akaraka_project

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
copy .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (optional)
bash setup_initial_data.sh

# Run server
python manage.py runserver
```

**URLs:**
- 🌐 Home: http://localhost:8000/
- 🔐 Admin: http://localhost:8000/admin/
- 📚 Courses: http://localhost:8000/courses/list/
- 👥 Community: http://localhost:8000/community/forum/
- ⭐ Achievements: http://localhost:8000/gamification/badges/

---

## 📦 Project Structure

```
akaraka_project/
├── akaraka/                    # Django project settings
│   ├── settings.py            # All configurations
│   ├── urls.py                # Main URL routing
│   └── wsgi.py
│
├── users/                      # User authentication & profiles
│   ├── models.py              # CustomUser, UserProfile
│   ├── views.py               # Login, Register, Profile
│   ├── forms.py               # Auth forms
│   └── admin.py               # Admin customization
│
├── courses/                    # Course management
│   ├── models.py              # Course, Lesson, Vocabulary
│   ├── views.py               # Dashboard, Lesson viewer
│   └── admin.py
│
├── exercises/                  # Exercise system
│   ├── models.py              # MCQ, Matching, Typing, Listening
│   ├── views.py               # Exercise handlers with grading
│   └── admin.py
│
├── gamification/              # XP, badges, streaks
│   ├── models.py              # Badge, Achievement, Tier
│   ├── views.py               # Leaderboards, achievements
│   └── admin.py
│
├── community/                 # Forum & testimonials
│   ├── models.py              # Post, Comment, Testimony
│   ├── views.py               # Forum, discussions
│   └── admin.py
│
├── payments/                  # Stripe integration
│   ├── models.py              # Subscription, Payment
│   ├── views.py               # Checkout, payment history
│   └── admin.py
│
├── certificates/              # Certificate generation
│   ├── models.py              # Certificate, Template
│   ├── views.py               # PDF generation
│   └── admin.py
│
├── templates/                 # HTML files
│   ├── base/
│   │   └── base.html          # Main layout
│   ├── users/                 # Auth pages
│   ├── courses/               # Course pages
│   ├── exercises/             # Exercise pages
│   ├── community/             # Forum pages
│   ├── gamification/          # Achievements
│   ├── payments/              # Payment pages
│   └── certificates/          # Certificate pages
│
├── static/                    # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── audio/
│
├── media/                     # User uploads
│   ├── certificates/
│   └── audio/
│
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🏗️ Database Models

### Users App
```
CustomUser
├── username, email, password (Django built-in)
├── current_level: 'beginner' | 'intermediate' | 'advanced'
├── total_xp: int (0+)
├── current_streak: int (daily)
├── longest_streak: int (record)
├── subscription_tier: 'free' | 'pro' | 'premium'
├── subscription_expires: datetime (null)
├── last_activity: datetime
└── [profile_picture, bio, language_preference]

UserProfile (one-to-one with CustomUser)
├── total_lessons_completed
├── total_exercises_completed
├── total_posts
├── followers (M2M)
└── created_at

EmailVerification
├── user (one-to-one)
├── token (unique)
└── created_at
```

### Courses App
```
Course
├── title, slug, description
├── level: 'beginner' | 'intermediate' | 'advanced'
├── is_paid: boolean
├── price: decimal
├── thumbnail: image
├── estimated_duration: int (minutes)
├── created_by (FK to User)
└── is_published: boolean

Lesson
├── course (FK)
├── title, slug, description
├── content_english, content_dari
├── audio_file: (pronunciation)
├── order: int
├── estimated_time: int (minutes)
└── is_published: boolean

Vocabulary
├── lesson (FK)
├── english_word, dari_word
├── pronunciation: string (IPA)
├── audio: file
├── part_of_speech: 'noun' | 'verb' | 'adjective'
├── example_english, example_dari
└── order: int

LessonProgress
├── user (FK)
├── lesson (FK - unique together)
├── is_completed: boolean
├── completion_time: datetime
├── attempts: int
├── xp_earned: int
└── last_accessed: datetime

CourseEnrollment
├── user (FK)
├── course (FK - unique together)
├── enrolled_at: datetime
├── is_completed: boolean
├── progress_percentage: int (0-100)
└── completion_date: datetime
```

### Exercises App
```
Exercise
├── title, description
├── exercise_type: 'mcq' | 'matching' | 'typing' | 'listening'
├── difficulty: 'easy' | 'medium' | 'hard'
├── xp_reward: int
└── is_published: boolean

MCQQuestion
├── exercise (FK)
├── question_english, question_dari
├── audio_file: (optional)
└── order: int

MCQOption
├── question (FK)
├── text_english, text_dari
├── is_correct: boolean
└── order: int

MatchingExercise (one-to-one with Exercise)
├── instruction_english, instruction_dari
└── pairs (reverse FK)

MatchingPair
├── matching (FK)
├── left_english, left_dari
├── right_english, right_dari
└── order: int

TypingExercise (one-to-one with Exercise)
├── instruction_english, instruction_dari
├── audio_file
└── prompts (reverse FK)

TypingPrompt
├── typing_exercise (FK)
├── sentence_english, sentence_dari
├── correct_answer: string
├── audio_file
└── order: int

ListeningExercise (one-to-one with Exercise)
├── instruction_english, instruction_dari
├── audio_file: (the listening content)
├── transcript_english, transcript_dari
└── questions (reverse FK)

ListeningQuestion
├── listening (FK)
├── question_english, question_dari
├── order: int
└── options (reverse FK)

ListeningOption
├── question (FK)
├── text_english, text_dari
├── is_correct: boolean
└── order: int

UserExerciseResponse
├── user (FK)
├── exercise (FK)
├── lesson (FK)
├── response_data: JSON
├── score: int (0-100)
├── is_correct: boolean
├── xp_earned: int
└── completed_at: datetime
```

### Gamification App
```
Badge
├── name (unique)
├── description
├── icon: image
├── badge_type: 'streak' | 'achievement' | 'milestone' | 'special'
├── requirement: string
├── requirement_value: int
├── xp_reward: int
└── is_active: boolean

UserBadge
├── user (FK)
├── badge (FK - unique together)
└── earned_at: datetime

Achievement
├── user (FK)
├── achievement_type: 'first_lesson' | 'level_up' | 'course_complete' | 'streak' | 'xp'
├── title, description
├── xp_earned: int
└── achieved_at: datetime

Leaderboard
├── user (FK)
├── period: 'daily' | 'weekly' | 'monthly' | 'all_time'
├── rank: int
├── xp: int
├── lessons_completed: int
├── exercises_completed: int
├── start_date, end_date: date
└── unique_together: (user, period, start_date)

DailyChallenge
├── challenge_type: 'complete_lesson' | 'complete_exercise' | 'daily_streak' | 'community_post'
├── description
├── xp_reward: int
└── is_active: boolean

UserDailyChallenge
├── user (FK)
├── challenge (FK)
├── progress: int
├── target: int
├── is_completed: boolean
├── completed_at: datetime
├── xp_earned: int
├── date: date
└── unique_together: (user, challenge, date)

Tier
├── name (unique)
├── description
├── min_xp (unique)
├── icon: image
└── perks: JSON

```

### Community App
```
Post
├── author (FK to User)
├── title, slug, content
├── post_type: 'question' | 'discussion' | 'resource' | 'testimonial'
├── tags: string (comma-separated)
├── likes (M2M with User)
├── views_count: int
├── is_pinned: boolean
├── is_featured: boolean
├── is_published: boolean
└── created_at, updated_at

Comment
├── post (FK)
├── author (FK)
├── content: text
├── likes (M2M)
├── parent_comment (self-FK - for replies)
├── is_approved: boolean
└── created_at, updated_at

Testimony
├── user (FK)
├── title, content
├── photo: image
├── rating: int (1-5)
├── achievement: string
├── is_published: boolean
├── likes (M2M)
└── created_at

Report
├── reporter (FK)
├── reported_post (FK - nullable)
├── reported_comment (FK - nullable)
├── report_type: 'spam' | 'harassment' | 'misinformation' | 'offensive' | 'other'
├── description
├── status: 'pending' | 'investigating' | 'resolved' | 'dismissed'
├── reviewed_by (FK - nullable)
├── review_notes
└── created_at, resolved_at

CommunityModerator
├── user (one-to-one)
├── is_active: boolean
├── appointed_at: datetime
└── reports_handled: int
```

### Payments App
```
Subscription
├── name (unique): 'free' | 'pro' | 'premium'
├── description
├── price_monthly, price_yearly: decimal
├── max_courses: int (-1 = unlimited)
├── course_access_level: 'beginner' | 'intermediate' | 'advanced'
├── features: JSON (list)
└── is_active: boolean

UserSubscription
├── user (one-to-one)
├── subscription (FK)
├── status: 'active' | 'cancelled' | 'expired'
├── start_date, end_date: datetime
├── auto_renew: boolean
├── stripe_customer_id: string
└── stripe_subscription_id: string

Payment
├── user (FK)
├── subscription (FK)
├── amount: decimal
├── currency: string (USD)
├── payment_method: 'stripe' | 'paypal' | 'local'
├── status: 'pending' | 'completed' | 'failed' | 'refunded'
├── transaction_id: string (unique)
├── stripe_charge_id: string
├── receipt: file
├── paid_at: datetime
└── created_at, updated_at

Invoice
├── payment (one-to-one)
├── invoice_number (unique)
├── pdf_file: file
└── issued_at: datetime
```

### Certificates App
```
Certificate
├── user (FK)
├── course (FK - unique together)
├── certificate_number (unique)
├── issue_date: datetime
├── pdf_file: file
├── score: int
├── is_verified: boolean
└── verification_code (unique)

CertificateTemplate
├── name (unique)
├── course (FK - nullable, if null = default for all)
├── template_html: text
├── custom_css: text
└── is_active: boolean
```

---

## 🔐 Authentication & Permissions

### Default Views Require Login
- Dashboard
- My Courses
- Exercise pages
- Create posts/comments
- Profile pages
- Certificates
- Subscription pages

### Public Views
- Home
- Course list (filtered by tier)
- Leaderboards
- Community forum (read-only)
- Registration/Login/Logout

### Subscription Access
```
Free Tier:
- Beginner courses only
- No certificates
- Limited community features

Pro Tier:
- Beginner + Intermediate
- Certificates
- Ad-free

Premium Tier:
- All courses (beginner, intermediate, advanced)
- All features
- Priority support
```

---

## 🎮 Gamification Logic

### XP Calculation
```python
XP_SETTINGS = {
    'lesson_complete': 10,
    'exercise_correct': 5,
    'post_like': 1,
    'comment': 2,
    'daily_streak_bonus': 5,
}

# Exercise XP based on score:
- 80-100%: Full reward
- 60-79%: 70% reward
- 40-59%: 50% reward
- <40%: 0 XP
```

### Streak Logic
```python
def update_streak():
    if last_activity was yesterday:
        current_streak += 1
    elif last_activity is older:
        current_streak = 1  # Reset
    
    # Update longest_streak if needed
    if current_streak > longest_streak:
        longest_streak = current_streak
```

### User Tiers (by XP)
- Beginner: 0 XP
- Intermediate: 500 XP
- Advanced: 1500 XP
- Expert: 3000 XP

---

## 🛠️ Key Views & URLs

### Users
```
GET  /                          → Home page
GET  /register/                 → Registration form
POST /register/                 → Create account
GET  /login/                    → Login form
POST /login/                    → Authenticate
GET  /logout/                   → Logout
GET  /profile/<username>/       → View profile
GET  /profile/<username>/edit/  → Edit profile
GET  /leaderboard/              → Global leaderboard
GET  /leaderboard/streaks/      → Streak leaderboard
```

### Courses
```
GET  /courses/dashboard/        → User dashboard
GET  /courses/list/             → Browse all courses
GET  /courses/<slug>/           → Course detail
GET  /courses/<course>/<lesson> → Lesson content
POST /courses/<slug>/enroll/    → Enroll in course
GET  /courses/my-courses/       → User's courses
```

### Exercises
```
GET/POST /exercises/mcq/<id>/<lesson_id>/       → MCQ exercise
GET/POST /exercises/matching/<id>/<lesson_id>/  → Matching exercise
GET/POST /exercises/typing/<id>/<lesson_id>/    → Typing exercise
GET/POST /exercises/listening/<id>/<lesson_id>/ → Listening exercise
```

### Gamification
```
GET /gamification/badges/          → All badges
GET /gamification/achievements/    → User achievements
GET /gamification/leaderboard/     → Global leaderboard
GET /gamification/leaderboard/weekly/  → Weekly ranking
GET /gamification/challenges/      → Daily challenges
GET /gamification/tier/            → User tier info
```

### Community
```
GET  /community/forum/              → Forum posts
GET  /community/post/<slug>/        → Post detail
POST /community/post/create/        → Create post
POST /community/post/<slug>/comment/ → Create comment
POST /community/post/<slug>/like/   → Like post
GET  /community/testimonies/        → Published testimonies
POST /community/testimonies/create/ → Create testimony
POST /community/report/             → Report content
```

### Payments
```
GET  /payments/plans/                       → Subscription plans
GET  /payments/checkout/<subscription_id>/  → Checkout page
POST /payments/checkout/<subscription_id>/  → Process payment
GET  /payments/history/                     → Payment history
GET  /payments/invoice/<payment_id>/        → Download invoice
POST /payments/cancel/                      → Cancel subscription
```

### Certificates
```
GET  /certificates/my-certificates/          → List certificates
GET  /certificates/<id>/                     → Certificate detail
GET  /certificates/<id>/download/            → Download PDF
GET  /certificates/verify/<code>/            → Verify certificate
POST /certificates/generate/<course_id>/     → Generate certificate
```

---

## 📄 Forms

All forms use Django's form system with Tailwind CSS styling:

- **AuthenticationForm**: Login
- **CustomUserCreationForm**: Registration
- **CustomUserChangeForm**: Profile edit
- **Exercise forms**: Dynamic based on exercise type

---

## 🎨 Templates

### Base Template (`templates/base/base.html`)
- Navigation bar with user menu
- Message display
- Footer with links
- Tailwind CSS utilities

### Key Templates
1. **users/home.html** - Landing page with features
2. **users/login.html** - Login form
3. **users/register.html** - Registration form
4. **courses/dashboard.html** - Main dashboard
5. **courses/course_detail.html** - Course overview
6. **courses/lesson_detail.html** - Lesson content + Dari toggle
7. **exercises/mcq_exercise.html** - MCQ interface
8. **community/forum.html** - Forum listing
9. **community/post_detail.html** - Post with comments
10. **gamification/leaderboard.html** - Rankings
11. **gamification/badges.html** - Achievements
12. **payments/subscription_plans.html** - Pricing
13. **certificates/my_certificates.html** - My certs

---

## 🔌 Stripe Integration

### Setup
1. Get API keys from Stripe dashboard
2. Add to `.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```

### Flow
1. User selects subscription
2. Redirect to checkout page
3. Stripe form created with public key
4. User submits payment
5. Backend processes with secret key
6. Create UserSubscription & Payment records
7. Update user tier

---

## 🚨 Security Notes

- ✅ CSRF tokens on all forms
- ✅ SQL injection prevention (Django ORM)
- ✅ XSS prevention (template escaping)
- ✅ Password hashing (PBKDF2)
- ✅ User permissions checked on views
- ✅ Email verification (optional)
- ⚠️ Enable SSL in production (`SECURE_SSL_REDIRECT=True`)
- ⚠️ Set strong `SECRET_KEY`
- ⚠️ Use environment variables for secrets

---

## 📊 Admin Commands

```bash
# Create superuser
python manage.py createsuperuser

# Create initial data
bash setup_initial_data.sh

# Database shell
python manage.py shell

# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json

# Check for issues
python manage.py check

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations
```

---

## 🐛 Common Issues & Fixes

### Issue: PostgreSQL connection error
**Fix**: Ensure PostgreSQL is running and credentials are correct in `.env`

### Issue: Static files not loading
**Fix**: Run `python manage.py collectstatic`

### Issue: Migrations not applying
**Fix**: Run `python manage.py migrate --no-input`

### Issue: Stripe payments failing
**Fix**: Check Stripe keys in `.env` and verify HTTPS in production

---

## 📈 Performance Tips

1. **Enable caching** for leaderboards:
   ```python
   from django.core.cache import cache
   cache.set('leaderboard', users, 3600)
   ```

2. **Use select_related** for foreign keys:
   ```python
   users = User.objects.select_related('profile')
   ```

3. **Use prefetch_related** for reverse relations:
   ```python
   posts = Post.objects.prefetch_related('comments')
   ```

4. **Index frequently filtered fields** (already done in models)

5. **Compress images** before upload

---

## 🚀 Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Set secure `SECRET_KEY`
- [ ] Enable SSL/HTTPS
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Configure database backups
- [ ] Set up email backend
- [ ] Add Stripe production keys
- [ ] Create admin user
- [ ] Run migrations
- [ ] Collect static files
- [ ] Set up error logging (Sentry)
- [ ] Monitor database performance
- [ ] Set up automated backups

---

## 📚 Next Steps to Customize

1. **Add custom branding** in base template
2. **Create course content** via admin panel
3. **Add exercise questions** with audio files
4. **Configure email notifications**
5. **Customize badges & achievements**
6. **Set up payment processing** (Stripe)
7. **Deploy to production** (Heroku, AWS, DigitalOcean)

---

## 💡 Code Quality

- Uses Django best practices
- Clean separation of concerns
- Reusable components
- Type hints in views
- Comprehensive admin interfaces
- Mobile-friendly templates

---

## 📞 Support Resources

- Django Docs: https://docs.djangoproject.com/
- Tailwind CSS: https://tailwindcss.com/
- Stripe API: https://stripe.com/docs/api
- PostgreSQL: https://www.postgresql.org/docs/

---

**Happy Learning! 🎓**

*Built with ❤️ for English learners worldwide*
