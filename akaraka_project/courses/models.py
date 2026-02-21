from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from datetime import datetime

User = get_user_model()


class Course(models.Model):
    """Main course model"""
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=255, help_text="Course title")
    slug = models.SlugField(unique=True)
    description = models.TextField(help_text="Course description")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, help_text="Difficulty level")
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', help_text="Course thumbnail")
    is_paid = models.BooleanField(default=False, help_text="Is this a paid course?")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_lessons = models.PositiveIntegerField(default=0)
    estimated_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='courses_created')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses_course'
        ordering = ['level', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_level_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_lesson_count(self):
        return self.lessons.count()


class Lesson(models.Model):
    """Individual lesson within a course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    content_english = models.TextField(help_text="English content/vocabulary")
    content_dari = models.TextField(blank=True, help_text="Dari translation/content (auto-translated if left empty)")
    audio_file = models.FileField(
        upload_to='audio/lessons/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a'])],
        help_text="Audio pronunciation file (MP3, WAV, OGG, M4A)"
    )
    image = models.ImageField(upload_to='lessons/images/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Lesson order within course")
    estimated_time = models.PositiveIntegerField(help_text="Time in minutes")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses_lesson'
        ordering = ['order']
        unique_together = ('course', 'slug')
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Vocabulary(models.Model):
    """Vocabulary words within a lesson"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='vocabulary')
    english_word = models.CharField(max_length=255)
    dari_word = models.CharField(max_length=255)
    example_english = models.TextField(blank=True)
    example_dari = models.TextField(blank=True)
    pronunciation = models.CharField(max_length=255, blank=True, help_text="IPA pronunciation")
    audio = models.FileField(
        upload_to='audio/vocabulary/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a'])]
    )
    image = models.ImageField(upload_to='vocabulary/', null=True, blank=True)
    part_of_speech = models.CharField(
        max_length=20,
        choices=[('noun', 'Noun'), ('verb', 'Verb'), ('adjective', 'Adjective'), ('other', 'Other')],
        default='noun'
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'courses_vocabulary'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.english_word} ({self.dari_word})"


class LessonProgress(models.Model):
    """Track user progress in lessons"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=False)
    completion_time = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    xp_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'courses_lessonprogress'
        unique_together = ('user', 'lesson')
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"
    
    def mark_completed(self, xp=10):
        """Mark lesson as completed and add XP"""
        self.is_completed = True
        self.completion_time = datetime.now()
        self.xp_earned = xp
        self.save()
        self.user.add_xp(xp)


class CourseEnrollment(models.Model):
    """Track course enrollments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'courses_courseenrollment'
        unique_together = ('user', 'course')
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    def calculate_progress(self):
        """Calculate completion percentage based on lesson progress"""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return self.progress_percentage
        completed = self.user.lesson_progress.filter(
            lesson__course=self.course,
            is_completed=True
        ).count()
        calculated = int((completed / total_lessons) * 100)
        # Update the stored progress percentage
        self.progress_percentage = calculated
        self.save(update_fields=['progress_percentage'])
        return calculated
    
    def get_progress(self):
        """Get current progress percentage (from stored field)"""
        return self.progress_percentage
    
    def update_progress(self, percentage):
        """Update progress percentage and mark complete if 100%"""
        self.progress_percentage = max(0, min(100, percentage))
        if self.progress_percentage >= 100 and not self.is_completed:
            self.is_completed = True
            self.completion_date = datetime.now()
        self.save()
        return self.progress_percentage

