from django.contrib import admin
from .models import (
    Exercise, ExerciseLesson, MCQQuestion, MCQOption, MatchingExercise, MatchingPair,
    TypingExercise, TypingPrompt, ListeningExercise, ListeningQuestion, ListeningOption,
    UserExerciseResponse
)


# Inline admins for nested editing
class ExerciseLessonInline(admin.TabularInline):
    model = ExerciseLesson
    extra = 1
    fields = ('lesson', 'order', 'is_required')
    raw_id_fields = ('lesson',)
    autocomplete_fields = ('lesson',)


class ListeningQuestionInline(admin.TabularInline):
    model = ListeningQuestion
    extra = 1
    fields = ('question_english', 'question_dari', 'order')


class ListeningExerciseInline(admin.StackedInline):
    model = ListeningExercise
    extra = 0
    fields = ('instruction_english', 'instruction_dari', 'audio_file', 'transcript_english', 'transcript_dari')
    inlines = [ListeningQuestionInline]


class MatchingExerciseInline(admin.StackedInline):
    model = MatchingExercise
    extra = 0


class TypingExerciseInline(admin.StackedInline):
    model = TypingExercise
    extra = 0


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'exercise_type', 'difficulty', 'xp_reward', 'is_published')
    list_filter = ('exercise_type', 'difficulty', 'is_published')
    search_fields = ('title', 'description')
    fields = ('title', 'description', 'exercise_type', 'difficulty', 'xp_reward', 'is_published')
    inlines = [ListeningExerciseInline, MatchingExerciseInline, TypingExerciseInline, ExerciseLessonInline]


@admin.register(ExerciseLesson)
class ExerciseLessonAdmin(admin.ModelAdmin):
    list_display = ('exercise_link', 'lesson_link', 'order', 'is_required')
    list_filter = ('is_required', 'lesson__course')
    search_fields = ('lesson__title', 'exercise__title', 'lesson__course__title')
    fields = ('lesson', 'exercise', 'order', 'is_required')
    raw_id_fields = ('lesson', 'exercise')
    autocomplete_fields = ('lesson', 'exercise')
    
    def exercise_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:exercises_exercise_change', args=[obj.exercise.id])
        return f'<a href="{url}">{obj.exercise}</a>'
    exercise_link.short_description = 'Exercise'
    exercise_link.allow_tags = True
    
    def lesson_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:courses_lesson_change', args=[obj.lesson.id])
        return f'<a href="{url}">{obj.lesson.title}</a> (in {obj.lesson.course.title})'
    lesson_link.short_description = 'Lesson'
    lesson_link.allow_tags = True


@admin.register(MCQQuestion)
class MCQQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_english', 'exercise', 'order')
    list_filter = ('exercise',)
    search_fields = ('question_english',)


@admin.register(MCQOption)
class MCQOptionAdmin(admin.ModelAdmin):
    list_display = ('text_english', 'question', 'is_correct', 'order')
    list_filter = ('is_correct',)
    search_fields = ('text_english',)


@admin.register(MatchingExercise)
class MatchingExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise',)


@admin.register(MatchingPair)
class MatchingPairAdmin(admin.ModelAdmin):
    list_display = ('left_english', 'right_english', 'matching', 'order')
    search_fields = ('left_english', 'right_english')


@admin.register(TypingExercise)
class TypingExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise',)


@admin.register(TypingPrompt)
class TypingPromptAdmin(admin.ModelAdmin):
    list_display = ('sentence_english', 'correct_answer', 'typing_exercise', 'order')
    search_fields = ('sentence_english', 'correct_answer')


@admin.register(ListeningExercise)
class ListeningExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise',)


@admin.register(ListeningQuestion)
class ListeningQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_english', 'listening', 'order')
    search_fields = ('question_english',)
    fields = ('listening', 'question_english', 'question_dari', 'order')


@admin.register(ListeningOption)
class ListeningOptionAdmin(admin.ModelAdmin):
    list_display = ('text_english', 'question', 'is_correct', 'order')
    list_filter = ('is_correct',)
    search_fields = ('text_english',)
    fields = ('question', 'text_english', 'text_dari', 'is_correct', 'order')


@admin.register(UserExerciseResponse)
class UserExerciseResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'score', 'is_correct', 'xp_earned', 'completed_at')
    list_filter = ('is_correct', 'completed_at')
    search_fields = ('user__username', 'exercise__title')
    readonly_fields = ('completed_at',)
