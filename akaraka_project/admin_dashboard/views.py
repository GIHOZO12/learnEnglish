from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from courses.models import Course, CourseEnrollment, Lesson
from community.models import Post, Comment
from payments.models import UserSubscription, Payment
from certificates.models import Certificate
from gamification.models import Badge, UserBadge
from exercises.models import UserExerciseResponse
from .decorators import admin_required

User = get_user_model()


@admin_required
def dashboard(request):
    """Main admin dashboard with statistics"""
    
    # User statistics
    total_users = User.objects.count()
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()
    new_users_week = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Course statistics
    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(is_published=True).count()
    total_enrollments = CourseEnrollment.objects.count()
    
    # Revenue statistics
    active_subscriptions = UserSubscription.objects.filter(status='active').count()
    
    # Activity statistics
    total_posts = Post.objects.count()
    total_certificates = Certificate.objects.count()
    total_badges_earned = UserBadge.objects.count()
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Top courses
    top_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]
    
    # Recent activity
    recent_exercises = UserExerciseResponse.objects.order_by('-completed_at')[:5]
    
    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'total_enrollments': total_enrollments,
        'active_subscriptions': active_subscriptions,
        'total_posts': total_posts,
        'total_certificates': total_certificates,
        'total_badges_earned': total_badges_earned,
        'recent_users': recent_users,
        'top_courses': top_courses,
        'recent_exercises': recent_exercises,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)


@admin_required
def user_management(request):
    """Manage all users"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'staff':
        users = users.filter(is_staff=True)
    elif status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_dashboard/user_management.html', context)


@admin_required
def user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    
    # User stats
    enrollments = user.course_enrollments.all()
    certificates = user.certificates.all()
    badges = user.earned_badges.all()
    posts = user.posts.all()
    
    # Learning progress
    overall_progress = user.get_learning_progress()
    lessons_progress = user.get_lessons_progress_percentage()
    total_lessons = user.get_total_lessons()
    completed_lessons = user.get_completed_lessons()
    
    context = {
        'user': user,
        'enrollments': enrollments,
        'certificates': certificates,
        'badges': badges,
        'posts': posts,
        'overall_progress': overall_progress,
        'lessons_progress': lessons_progress,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
    }
    return render(request, 'admin_dashboard/user_detail.html', context)


@admin_required
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@admin_required
def toggle_staff_status(request, user_id):
    """Toggle user staff status"""
    user = get_object_or_404(User, id=user_id)
    user.is_staff = not user.is_staff
    user.save()
    
    status = "promoted to staff" if user.is_staff else "removed from staff"
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@admin_required
def course_management(request):
    """Manage all courses"""
    courses = Course.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'published':
        courses = courses.filter(is_published=True)
    elif status_filter == 'draft':
        courses = courses.filter(is_published=False)
    elif status_filter == 'paid':
        courses = courses.filter(is_paid=True)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(title__icontains=search_query)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(courses, 15)
    page = request.GET.get('page', 1)
    courses = paginator.get_page(page)
    
    context = {
        'courses': courses,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_dashboard/course_management.html', context)


@admin_required
def course_detail(request, course_id):
    """View course details"""
    course = get_object_or_404(Course, id=course_id)
    
    enrollments = course.enrollments.all()
    lessons = course.lessons.all()
    
    context = {
        'course': course,
        'enrollments': enrollments,
        'lessons': lessons,
    }
    return render(request, 'admin_dashboard/course_detail.html', context)


@admin_required
def toggle_course_publish(request, course_id):
    """Toggle course publication status"""
    course = get_object_or_404(Course, id=course_id)
    course.is_published = not course.is_published
    course.save()
    
    status = "published" if course.is_published else "unpublished"
    messages.success(request, f'Course "{course.title}" has been {status}.')
    return redirect('admin_dashboard:course_detail', course_id=course_id)


@admin_required
def community_management(request):
    """Manage community posts and comments"""
    posts = Post.objects.all().order_by('-created_at')
    
    # Filter
    filter_type = request.GET.get('filter', '')
    if filter_type == 'reported':
        posts = posts.filter(is_reported=True)
    elif filter_type == 'featured':
        posts = posts.filter(is_featured=True)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(title__icontains=search_query)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(posts, 20)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'filter_type': filter_type,
    }
    return render(request, 'admin_dashboard/community_management.html', context)


@admin_required
def post_detail(request, post_id):
    """View post details and comments"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'admin_dashboard/post_detail.html', context)


@admin_required
def delete_post(request, post_id):
    """Delete a post"""
    post = get_object_or_404(Post, id=post_id)
    post_title = post.title
    post.delete()
    messages.success(request, f'Post "{post_title}" has been deleted.')
    return redirect('admin_dashboard:community_management')


@admin_required
def subscription_management(request):
    """Manage subscriptions"""
    subscriptions = UserSubscription.objects.all().order_by('-start_date')
    
    # Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        subscriptions = subscriptions.filter(status=status_filter)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(subscriptions, 20)
    page = request.GET.get('page', 1)
    subscriptions = paginator.get_page(page)
    
    # Stats
    active_subs = UserSubscription.objects.filter(status='active').count()
    cancelled_subs = UserSubscription.objects.filter(status='cancelled').count()
    
    context = {
        'subscriptions': subscriptions,
        'status_filter': status_filter,
        'active_count': active_subs,
        'cancelled_count': cancelled_subs,
    }
    return render(request, 'admin_dashboard/subscription_management.html', context)


@admin_required
def analytics(request):
    """View analytics and reports"""
    
    # Time period filter
    period = request.GET.get('period', '30')
    
    if period == '7':
        start_date = timezone.now() - timedelta(days=7)
    elif period == '90':
        start_date = timezone.now() - timedelta(days=90)
    else:  # 30 days default
        start_date = timezone.now() - timedelta(days=30)
    
    # User growth
    new_users = User.objects.filter(date_joined__gte=start_date).count()
    
    # Course enrollments growth
    new_enrollments = CourseEnrollment.objects.filter(
        enrolled_at__gte=start_date
    ).count()
    
    # Course completion rate
    total_enrollments = CourseEnrollment.objects.count()
    completed_enrollments = CourseEnrollment.objects.filter(
        is_completed=True
    ).count()
    completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
    
    # Most popular courses
    popular_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:10]
    
    # Most active users
    active_users = User.objects.annotate(
        exercise_count=Count('exercise_responses')
    ).order_by('-exercise_count')[:10]
    
    context = {
        'period': period,
        'new_users': new_users,
        'new_enrollments': new_enrollments,
        'completion_rate': round(completion_rate, 2),
        'popular_courses': popular_courses,
        'active_users': active_users,
    }
    return render(request, 'admin_dashboard/analytics.html', context)


# ============ COURSE CRUD OPERATIONS ============

@admin_required
def create_course(request):
    """Create a new course"""
    if request.method == 'POST':
        try:
            course = Course(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                level=request.POST.get('level', 'beginner'),
                is_paid=request.POST.get('is_paid') == 'on',
                price=request.POST.get('price', 0),
                estimated_duration=request.POST.get('estimated_duration', 0),
                created_by=request.user,
                is_published=request.POST.get('is_published') == 'on',
            )
            if 'thumbnail' in request.FILES:
                course.thumbnail = request.FILES['thumbnail']
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('admin_dashboard:course_detail', course_id=course.id)
        except Exception as e:
            messages.error(request, f'Error creating course: {str(e)}')
    
    context = {}
    return render(request, 'admin_dashboard/create_course.html', context)


@admin_required
def edit_course(request, course_id):
    """Edit an existing course"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        try:
            course.title = request.POST.get('title', course.title)
            course.description = request.POST.get('description', course.description)
            course.level = request.POST.get('level', course.level)
            course.is_paid = request.POST.get('is_paid') == 'on'
            course.price = request.POST.get('price', course.price)
            course.estimated_duration = request.POST.get('estimated_duration', course.estimated_duration)
            course.is_published = request.POST.get('is_published') == 'on'
            
            if 'thumbnail' in request.FILES:
                course.thumbnail = request.FILES['thumbnail']
            
            course.save()
            messages.success(request, f'Course "{course.title}" updated successfully!')
            return redirect('admin_dashboard:course_detail', course_id=course.id)
        except Exception as e:
            messages.error(request, f'Error updating course: {str(e)}')
    
    context = {'course': course}
    return render(request, 'admin_dashboard/edit_course.html', context)


@admin_required
def delete_course(request, course_id):
    """Delete a course"""
    course = get_object_or_404(Course, id=course_id)
    course_title = course.title
    course.delete()
    messages.success(request, f'Course "{course_title}" has been deleted.')
    return redirect('admin_dashboard:course_management')


# ============ EXERCISE CRUD OPERATIONS ============

@admin_required
def exercise_management(request):
    """Manage all exercises"""
    from exercises.models import Exercise
    
    exercises = Exercise.objects.all().order_by('-created_at')
    
    # Filter by type
    exercise_type = request.GET.get('type', '')
    if exercise_type:
        exercises = exercises.filter(exercise_type=exercise_type)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        exercises = exercises.filter(title__icontains=search_query)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(exercises, 15)
    page = request.GET.get('page', 1)
    exercises = paginator.get_page(page)
    
    context = {
        'exercises': exercises,
        'search_query': search_query,
        'exercise_type': exercise_type,
    }
    return render(request, 'admin_dashboard/exercise_management.html', context)


@admin_required
def create_exercise(request):
    """Create a new exercise"""
    from exercises.models import Exercise
    
    if request.method == 'POST':
        try:
            exercise = Exercise(
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                exercise_type=request.POST.get('exercise_type', 'mcq'),
                difficulty=request.POST.get('difficulty', 'easy'),
                xp_reward=request.POST.get('xp_reward', 5),
                is_published=request.POST.get('is_published') == 'on',
            )
            exercise.save()
            messages.success(request, f'Exercise "{exercise.title}" created successfully!')
            return redirect('admin_dashboard:exercise_detail', exercise_id=exercise.id)
        except Exception as e:
            messages.error(request, f'Error creating exercise: {str(e)}')
    
    context = {}
    return render(request, 'admin_dashboard/create_exercise.html', context)


@admin_required
def exercise_detail(request, exercise_id):
    """View exercise details"""
    from exercises.models import Exercise, ExerciseLesson, ListeningExercise
    from courses.models import Lesson
    from gtts import gTTS
    import os
    
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    # Handle creating/updating listening exercise
    if request.method == 'POST' and exercise.exercise_type == 'listening':
        try:
            if 'create_listening' in request.POST:
                # Create new listening exercise
                listening_exercise, created = ListeningExercise.objects.get_or_create(exercise=exercise)
                listening_exercise.instruction_english = request.POST.get('instruction_english')
                listening_exercise.instruction_dari = request.POST.get('instruction_dari')
                listening_exercise.transcript_english = request.POST.get('transcript_english', '')
                listening_exercise.transcript_dari = request.POST.get('transcript_dari', '')
                
                # Handle TTS generation
                if 'generate_audio_en' in request.POST:
                    text = request.POST.get('instruction_english', '')
                    if text:
                        tts = gTTS(text=text, lang='en', slow=False)
                        filename = f'listening_{exercise.id}_en.mp3'
                        filepath = os.path.join('media', 'audio', 'listening', filename)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        tts.save(filepath)
                        listening_exercise.audio_file = f'audio/listening/{filename}'
                        messages.info(request, '✓ Audio generated from English text')
                
                elif 'generate_audio_dari' in request.POST:
                    text = request.POST.get('instruction_dari', '')
                    if text:
                        tts = gTTS(text=text, lang='ps', slow=False)  # ps = Pashto (closest to Dari)
                        filename = f'listening_{exercise.id}_dari.mp3'
                        filepath = os.path.join('media', 'audio', 'listening', filename)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        tts.save(filepath)
                        listening_exercise.audio_file = f'audio/listening/{filename}'
                        messages.info(request, '✓ Audio generated from Dari text')
                
                elif 'audio_file' in request.FILES:
                    listening_exercise.audio_file = request.FILES['audio_file']
                
                listening_exercise.save()
                messages.success(request, 'Listening exercise created successfully!')
                return redirect('admin_dashboard:exercise_detail', exercise_id=exercise.id)
            
            elif 'update_listening' in request.POST:
                # Update existing listening exercise
                listening_id = request.POST.get('listening_id')
                listening_exercise = get_object_or_404(ListeningExercise, id=listening_id)
                
                listening_exercise.instruction_english = request.POST.get('instruction_english')
                listening_exercise.instruction_dari = request.POST.get('instruction_dari')
                listening_exercise.transcript_english = request.POST.get('transcript_english', '')
                listening_exercise.transcript_dari = request.POST.get('transcript_dari', '')
                
                # Handle TTS generation
                if 'generate_audio_en' in request.POST:
                    text = request.POST.get('instruction_english', '')
                    if text:
                        tts = gTTS(text=text, lang='en', slow=False)
                        filename = f'listening_{exercise.id}_en.mp3'
                        filepath = os.path.join('media', 'audio', 'listening', filename)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        tts.save(filepath)
                        listening_exercise.audio_file = f'audio/listening/{filename}'
                        messages.info(request, '✓ Audio generated from English text')
                
                elif 'generate_audio_dari' in request.POST:
                    text = request.POST.get('instruction_dari', '')
                    if text:
                        tts = gTTS(text=text, lang='ps', slow=False)  # ps = Pashto (closest to Dari)
                        filename = f'listening_{exercise.id}_dari.mp3'
                        filepath = os.path.join('media', 'audio', 'listening', filename)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        tts.save(filepath)
                        listening_exercise.audio_file = f'audio/listening/{filename}'
                        messages.info(request, '✓ Audio generated from Dari text')
                
                elif 'audio_file' in request.FILES:
                    listening_exercise.audio_file = request.FILES['audio_file']
                
                listening_exercise.save()
                messages.success(request, 'Listening exercise updated successfully!')
                return redirect('admin_dashboard:exercise_detail', exercise_id=exercise.id)
            
            elif 'add_lesson' in request.POST:
                # Handle adding a lesson link
                lesson_id = request.POST.get('lesson_id')
                order = request.POST.get('order', 0)
                is_required = request.POST.get('is_required') == 'on'
                
                lesson = get_object_or_404(Lesson, id=lesson_id)
                
                # Check if already linked
                if ExerciseLesson.objects.filter(exercise=exercise, lesson=lesson).exists():
                    messages.warning(request, 'This exercise is already linked to this lesson.')
                else:
                    ExerciseLesson.objects.create(
                        exercise=exercise,
                        lesson=lesson,
                        order=order,
                        is_required=is_required
                    )
                    messages.success(request, f'Exercise linked to lesson "{lesson.title}"')
                return redirect('admin_dashboard:exercise_detail', exercise_id=exercise.id)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('admin_dashboard:exercise_detail', exercise_id=exercise.id)
    
    # Get listening exercise if it's a listening type
    listening_exercise = None
    if exercise.exercise_type == 'listening':
        listening_exercise = ListeningExercise.objects.filter(exercise=exercise).first()
    
    # Get linked lessons
    linked_lessons = exercise.lesson_links.all().select_related('lesson', 'lesson__course')
    all_lessons = Lesson.objects.select_related('course').filter(is_published=True)
    
    # Get lessons not yet linked
    linked_lesson_ids = linked_lessons.values_list('lesson_id', flat=True)
    available_lessons = all_lessons.exclude(id__in=linked_lesson_ids)
    
    context = {
        'exercise': exercise,
        'listening_exercise': listening_exercise,
        'linked_lessons': linked_lessons,
        'available_lessons': available_lessons,
    }
    return render(request, 'admin_dashboard/exercise_detail.html', context)


@admin_required
def edit_exercise(request, exercise_id):
    """Edit an existing exercise"""
    from exercises.models import Exercise
    
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    if request.method == 'POST':
        try:
            exercise.title = request.POST.get('title', exercise.title)
            exercise.description = request.POST.get('description', exercise.description)
            exercise.difficulty = request.POST.get('difficulty', exercise.difficulty)
            exercise.xp_reward = request.POST.get('xp_reward', exercise.xp_reward)
            exercise.is_published = request.POST.get('is_published') == 'on'
            exercise.save()
            
            messages.success(request, f'Exercise "{exercise.title}" updated successfully!')
            return redirect('admin_dashboard:exercise_detail', exercise_id=exercise.id)
        except Exception as e:
            messages.error(request, f'Error updating exercise: {str(e)}')
    
    context = {'exercise': exercise}
    return render(request, 'admin_dashboard/edit_exercise.html', context)


@admin_required
def delete_exercise(request, exercise_id):
    """Delete an exercise"""
    from exercises.models import Exercise
    
    exercise = get_object_or_404(Exercise, id=exercise_id)
    exercise_title = exercise.title
    exercise.delete()
    messages.success(request, f'Exercise "{exercise_title}" has been deleted.')
    return redirect('admin_dashboard:exercise_management')


# ============ LESSON MANAGEMENT ============

@admin_required
def lesson_management(request, course_id):
    """Manage lessons for a course"""
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all().order_by('order')
    
    context = {
        'course': course,
        'lessons': lessons,
    }
    return render(request, 'admin_dashboard/lesson_management.html', context)


@admin_required
def lesson_detail(request, lesson_id):
    """View and manage exercises for a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    exercises = lesson.exercises.all()
    
    # All available exercises to add
    from exercises.models import Exercise
    all_exercises = Exercise.objects.filter(is_published=True)
    assigned_exercise_ids = exercises.values_list('exercise_id', flat=True)
    available_exercises = all_exercises.exclude(id__in=assigned_exercise_ids)
    
    context = {
        'lesson': lesson,
        'course': course,
        'exercises': exercises,
        'available_exercises': available_exercises,
    }
    return render(request, 'admin_dashboard/lesson_detail.html', context)


@admin_required
def add_exercise_to_lesson(request, lesson_id):
    """Add an exercise to a lesson"""
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        exercise_id = request.POST.get('exercise_id')
        
        from exercises.models import Exercise, ExerciseLesson
        exercise = get_object_or_404(Exercise, id=exercise_id)
        
        # Check if already exists
        if not ExerciseLesson.objects.filter(lesson=lesson, exercise=exercise).exists():
            ExerciseLesson.objects.create(
                lesson=lesson,
                exercise=exercise,
                order=lesson.exercises.count() + 1
            )
            messages.success(request, f'Exercise "{exercise.title}" added to lesson!')
        else:
            messages.warning(request, 'This exercise is already in this lesson!')
    
    return redirect('admin_dashboard:lesson_detail', lesson_id=lesson_id)


@admin_required
def remove_exercise_from_lesson(request, lesson_id, exercise_lesson_id):
    """Remove an exercise from a lesson"""
    from exercises.models import ExerciseLesson
    
    exercise_lesson = get_object_or_404(ExerciseLesson, id=exercise_lesson_id)
    exercise_title = exercise_lesson.exercise.title
    exercise_lesson.delete()
    messages.success(request, f'Exercise "{exercise_title}" removed from lesson!')
    return redirect('admin_dashboard:lesson_detail', lesson_id=lesson_id)


@admin_required
def remove_lesson_from_exercise(request, exercise_id, exercise_lesson_id):
    """Remove a lesson link from an exercise"""
    from exercises.models import ExerciseLesson
    
    exercise_lesson = get_object_or_404(ExerciseLesson, id=exercise_lesson_id)
    lesson_title = exercise_lesson.lesson.title
    exercise_lesson.delete()
    messages.success(request, f'Lesson "{lesson_title}" unlinked from exercise!')
    return redirect('admin_dashboard:exercise_detail', exercise_id=exercise_id)
