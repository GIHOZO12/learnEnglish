from django.contrib import admin
from .models import Course, Lesson, Vocabulary, LessonProgress, CourseEnrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'is_published', 'is_paid', 'price', 'created_at')
    list_filter = ('level', 'is_published', 'is_paid', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published', 'estimated_time')
    list_filter = ('course', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('course',)


@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('english_word', 'dari_word', 'lesson', 'part_of_speech', 'order')
    list_filter = ('part_of_speech', 'lesson__course')
    search_fields = ('english_word', 'dari_word')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'attempts', 'xp_earned', 'last_accessed')
    list_filter = ('is_completed', 'last_accessed')
    search_fields = ('user__username', 'lesson__title')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'is_completed', 'progress_percentage')
    list_filter = ('is_completed', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
