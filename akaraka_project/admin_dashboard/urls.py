from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/toggle-staff/', views.toggle_staff_status, name='toggle_staff_status'),
    
    # Course Management
    path('courses/', views.course_management, name='course_management'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('courses/<int:course_id>/toggle-publish/', views.toggle_course_publish, name='toggle_course_publish'),
    path('courses/<int:course_id>/lessons/', views.lesson_management, name='lesson_management'),
    path('courses/<int:course_id>/lessons/create/', views.create_lesson, name='create_lesson'),
    
    # Lesson Management
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('lessons/<int:lesson_id>/add-exercise/', views.add_exercise_to_lesson, name='add_exercise_to_lesson'),
    path('lessons/<int:lesson_id>/remove-exercise/<int:exercise_lesson_id>/', views.remove_exercise_from_lesson, name='remove_exercise_from_lesson'),
    
    # Exercise Management
    path('exercises/', views.exercise_management, name='exercise_management'),
    path('exercises/create/', views.create_exercise, name='create_exercise'),
    path('exercises/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    path('exercises/<int:exercise_id>/edit/', views.edit_exercise, name='edit_exercise'),
    path('exercises/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),
    path('exercises/<int:exercise_id>/remove-lesson/<int:exercise_lesson_id>/', views.remove_lesson_from_exercise, name='remove_lesson_from_exercise'),
    
    # Community Management
    path('community/', views.community_management, name='community_management'),
    path('community/posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('community/posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
    # Subscription Management
    path('subscriptions/', views.subscription_management, name='subscription_management'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
