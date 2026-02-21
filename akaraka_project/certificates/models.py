from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course
from datetime import datetime

User = get_user_model()


class Certificate(models.Model):
    """Course completion certificate"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_number = models.CharField(max_length=255, unique=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    score = models.PositiveIntegerField(default=100, help_text="Final course score")
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=50, unique=True, blank=True)
    
    class Meta:
        db_table = 'certificates_certificate'
        unique_together = ('user', 'course')
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"Certificate: {self.user.username} - {self.course.title}"
    
    def get_verification_url(self):
        return f"https://akaraka.com/verify/{self.verification_code}/"


class CertificateTemplate(models.Model):
    """Template for certificate design"""
    name = models.CharField(max_length=255, unique=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, help_text="If null, applies to all courses")
    template_html = models.TextField(help_text="HTML template with {user_name}, {course_title}, {date}, etc.")
    custom_css = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'certificates_certificatetemplate'
    
    def __str__(self):
        return self.name
