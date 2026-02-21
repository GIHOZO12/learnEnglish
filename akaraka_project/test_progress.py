#!/usr/bin/env python
"""Script to test user progress functionality"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akaraka.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Course, CourseEnrollment

User = get_user_model()

print("=" * 60)
print("USER PROGRESS TEST")
print("=" * 60)

# Get user with ID 1
try:
    user = User.objects.get(id=1)
    print(f"\n✓ User found: {user.username} (ID: {user.id})")
except User.DoesNotExist:
    print("\n✗ User with ID 1 not found")
    exit(1)

# Get courses
courses = Course.objects.all()
if not courses.exists():
    print("✗ No courses found in database")
    exit(1)

print(f"✓ Found {courses.count()} course(s)")

# Create enrollments with progress
print("\n" + "-" * 60)
print("Setting up course enrollments with progress...")
print("-" * 60)

for i, course in enumerate(courses[:3], 1):  # Test with up to 3 courses
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=user,
        course=course,
        defaults={'progress_percentage': 0}
    )
    
    # Set different progress for each course
    progress = (i * 30) % 100
    enrollment.update_progress(progress)
    
    status = "Created" if created else "Updated"
    print(f"  {status}: {course.title}")
    print(f"    └─ Progress: {enrollment.progress_percentage}%")

# Check results
print("\n" + "-" * 60)
print("PROGRESS SUMMARY")
print("-" * 60)

enrollments = user.course_enrollments.all()
print(f"\nUser: {user.username}")
print(f"Enrollments: {enrollments.count()}")

if enrollments.exists():
    print("\nCourse Progress:")
    for enrollment in enrollments:
        print(f"  • {enrollment.course.title}")
        print(f"    └─ {enrollment.progress_percentage}%")
    
    overall = user.get_learning_progress()
    print(f"\nOverall Learning Progress: {overall}%")
    
    completed = user.get_completed_lessons()
    total = user.get_total_lessons()
    lessons_progress = user.get_lessons_progress_percentage()
    print(f"Lessons Progress: {completed}/{total} ({lessons_progress}%)")
else:
    print("No enrollments found")

print("\n" + "=" * 60)
print("✓ Test complete! Check the admin panel to see progress bars")
print("=" * 60)
