from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Post(models.Model):
    """Community posts/discussions"""
    
    POST_TYPES = [
        ('question', 'Question'),
        ('discussion', 'Discussion'),
        ('resource', 'Resource Share'),
        ('testimonial', 'Testimonial'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='discussion')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    views_count = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'community_post'
        ordering = ['-is_pinned', '-is_featured', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_like_count(self):
        return self.likes.count()
    
    def get_comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    """Comments on posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        help_text="For nested/reply comments"
    )
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'community_comment'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    def get_like_count(self):
        return self.likes.count()


class Testimony(models.Model):
    """User testimonials/learning stories"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonies')
    title = models.CharField(max_length=255)
    content = models.TextField()
    photo = models.ImageField(upload_to='testimonies/', null=True, blank=True)
    rating = models.PositiveIntegerField(choices=[(i, f'{i} Stars') for i in range(1, 6)])
    achievement = models.CharField(max_length=255, blank=True, help_text="What did you achieve?")
    is_published = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_testimonies', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'community_testimony'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Testimony by {self.user.username}"


class Report(models.Model):
    """Report inappropriate content"""
    
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('misinformation', 'Misinformation'),
        ('offensive', 'Offensive Content'),
        ('other', 'Other'),
    ]
    
    REPORT_STATUS = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    reported_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'community_report'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report by {self.reporter.username} - {self.report_type}"


class CommunityModerator(models.Model):
    """Community moderators"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='moderator_profile')
    is_active = models.BooleanField(default=True)
    appointed_at = models.DateTimeField(auto_now_add=True)
    reports_handled = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'community_moderator'
    
    def __str__(self):
        return f"Moderator: {self.user.username}"
