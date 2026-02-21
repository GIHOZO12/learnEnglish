from django.urls import path
from .views import (
    DashboardView, CourseListView, CourseDetailView, LessonDetailView,
    EnrollCourseView, MyCoursesView, MyProgressView
)

app_name = 'courses'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('my-progress/', MyProgressView.as_view(), name='my_progress'),
    path('list/', CourseListView.as_view(), name='course_list'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('<slug:slug>/enroll/', EnrollCourseView.as_view(), name='enroll'),
    path('my-courses/', MyCoursesView.as_view(), name='my_courses'),
]
