from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from .models import Course, Lesson, Vocabulary, LessonProgress, CourseEnrollment
from exercises.models import ExerciseLesson


class DashboardView(LoginRequiredMixin, View):
    """User dashboard"""
    def get(self, request):
        user = request.user
        user.update_last_activity()
        
        enrollments = CourseEnrollment.objects.filter(user=user)
        available_courses = Course.objects.filter(is_published=True)
        
        # Filter based on user level and subscription
        if not user.is_premium():
            available_courses = available_courses.filter(level='beginner')
        
        context = {
            'enrollments': enrollments,
            'available_courses': available_courses[:6],
            'total_xp': user.total_xp,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
        }
        return render(request, 'courses/dashboard.html', context)


class MyProgressView(LoginRequiredMixin, View):
    """User learning progress dashboard"""
    def get(self, request):
        user = request.user
        
        # Get enrollments
        enrollments = user.course_enrollments.all()
        
        # Get progress data
        overall_progress = user.get_learning_progress()
        lessons_progress = user.get_lessons_progress_percentage()
        completed_lessons = user.get_completed_lessons()
        total_lessons = user.get_total_lessons()
        
        # Get certificates and badges
        certificates = user.certificates.all()
        badges = user.earned_badges.all()
        
        context = {
            'enrollments': enrollments,
            'overall_progress': overall_progress,
            'lessons_progress': lessons_progress,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'certificates': certificates,
            'badges': badges,
        }
        return render(request, 'courses/my_progress.html', context)


class CourseListView(ListView):
    """Browse all courses"""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)
        
        # Filter by level
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Filter by free/paid
        free_only = self.request.GET.get('free_only')
        if free_only == 'on':
            queryset = queryset.filter(is_paid=False)
        
        # Apply user tier restrictions
        if self.request.user.is_authenticated and not self.request.user.is_premium():
            queryset = queryset.filter(level='beginner')
        
        return queryset.order_by('-created_at')


class CourseDetailView(DetailView):
    """Course detail page"""
    model = Course
    template_name = 'courses/course_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['lessons'] = course.lessons.all().order_by('order')
        
        if self.request.user.is_authenticated:
            enrollment = CourseEnrollment.objects.filter(
                user=self.request.user,
                course=course
            ).first()
            context['enrollment'] = enrollment
            context['is_enrolled'] = enrollment is not None
        
        return context


class LessonDetailView(LoginRequiredMixin, View):
    """Lesson detail with content and Dari toggle"""
    def get(self, request, course_slug, lesson_slug):
        course = get_object_or_404(Course, slug=course_slug, is_published=True)
        lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug, is_published=True)
        
        # Check access
        enrollment = CourseEnrollment.objects.filter(user=request.user, course=course).first()
        if not enrollment and course.is_paid and not request.user.is_premium():
            messages.error(request, 'You must enroll to access this course.')
            return redirect('courses:course_detail', slug=course.slug)
        
        # Get or create progress
        progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        progress.attempts += 1
        progress.save()
        
        # Get vocabulary
        vocabulary = lesson.vocabulary.all().order_by('order')
        
        # Get exercises for this lesson
        exercises = ExerciseLesson.objects.filter(lesson=lesson)
        
        context = {
            'course': course,
            'lesson': lesson,
            'vocabulary': vocabulary,
            'exercises': exercises,
            'progress': progress,
            'show_dari': request.GET.get('dari', 'true') == 'true',
        }
        
        return render(request, 'courses/lesson_detail.html', context)


class EnrollCourseView(LoginRequiredMixin, View):
    """Enroll in a course"""
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        
        # Check if already enrolled
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        if created:
            messages.success(request, f'You have enrolled in {course.title}!')
        else:
            messages.info(request, f'You are already enrolled in {course.title}.')
        
        return redirect('courses:course_detail', slug=course.slug)


class MyCoursesView(LoginRequiredMixin, ListView):
    """User's enrolled courses"""
    template_name = 'courses/my_courses.html'
    context_object_name = 'enrollments'
    paginate_by = 12
    
    def get_queryset(self):
        return CourseEnrollment.objects.filter(user=self.request.user).select_related('course')
