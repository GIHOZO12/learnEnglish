from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Lesson, Course
from datetime import datetime

User = get_user_model()


class Exercise(models.Model):
    """Base exercise model"""
    
    EXERCISE_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('matching', 'Matching'),
        ('typing', 'Typing'),
        ('listening', 'Listening'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    difficulty = models.CharField(
        max_length=20,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='easy'
    )
    xp_reward = models.PositiveIntegerField(default=5)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exercises_exercise'
    
    def __str__(self):
        return f"{self.title} ({self.get_exercise_type_display()})"


class ExerciseLesson(models.Model):
    """Link exercises to lessons"""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='lesson_links')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'exercises_exerciselesson'
        unique_together = ('exercise', 'lesson')
    
    def __str__(self):
        return f"{self.lesson.title} - {self.exercise.title}"


class MCQQuestion(models.Model):
    """Multiple Choice Question"""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='mcq_questions', limit_choices_to={'exercise_type': 'mcq'})
    question_english = models.TextField()
    question_dari = models.TextField()
    audio = models.FileField(upload_to='audio/exercises/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True)
    
    class Meta:
        db_table = 'exercises_mcqquestion'
        ordering = ['order']
    
    def __str__(self):
        return f"MCQ: {self.question_english[:50]}"


class MCQOption(models.Model):
    """MCQ Answer options"""
    question = models.ForeignKey(MCQQuestion, on_delete=models.CASCADE, related_name='options')
    text_english = models.CharField(max_length=500)
    text_dari = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'exercises_mcqoption'
        ordering = ['order']
    
    def __str__(self):
        return self.text_english


class MatchingExercise(models.Model):
    """Matching exercise (pair items)"""
    exercise = models.OneToOneField(Exercise, on_delete=models.CASCADE, related_name='matching', limit_choices_to={'exercise_type': 'matching'})
    instruction_english = models.TextField()
    instruction_dari = models.TextField()
    
    class Meta:
        db_table = 'exercises_matchingexercise'
    
    def __str__(self):
        return f"Matching: {self.exercise.title}"


class MatchingPair(models.Model):
    """Individual matching pairs"""
    matching = models.ForeignKey(MatchingExercise, on_delete=models.CASCADE, related_name='pairs')
    left_english = models.CharField(max_length=500)
    left_dari = models.CharField(max_length=500, blank=True)
    right_english = models.CharField(max_length=500)
    right_dari = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'exercises_matchingpair'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.left_english} <-> {self.right_english}"


class TypingExercise(models.Model):
    """Typing/Fill-in-the-blank exercise"""
    exercise = models.OneToOneField(Exercise, on_delete=models.CASCADE, related_name='typing', limit_choices_to={'exercise_type': 'typing'})
    instruction_english = models.TextField()
    instruction_dari = models.TextField()
    audio = models.FileField(upload_to='audio/exercises/', null=True, blank=True)
    
    class Meta:
        db_table = 'exercises_typingexercise'
    
    def __str__(self):
        return f"Typing: {self.exercise.title}"


class TypingPrompt(models.Model):
    """Typing exercise prompts"""
    typing_exercise = models.ForeignKey(TypingExercise, on_delete=models.CASCADE, related_name='prompts')
    sentence_english = models.TextField()
    sentence_dari = models.TextField()
    correct_answer = models.CharField(max_length=500)
    audio = models.FileField(upload_to='audio/exercises/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'exercises_typingprompt'
        ordering = ['order']
    
    def __str__(self):
        return self.sentence_english[:50]


class ListeningExercise(models.Model):
    """Listening comprehension exercise"""
    exercise = models.OneToOneField(Exercise, on_delete=models.CASCADE, related_name='listening', limit_choices_to={'exercise_type': 'listening'})
    instruction_english = models.TextField()
    instruction_dari = models.TextField()
    audio_file = models.FileField(upload_to='audio/listening/')
    transcript_english = models.TextField(blank=True)
    transcript_dari = models.TextField(blank=True)
    
    class Meta:
        db_table = 'exercises_listeningexercise'
    
    def __str__(self):
        return f"Listening: {self.exercise.title}"


class ListeningQuestion(models.Model):
    """Questions for listening exercise"""
    listening = models.ForeignKey(ListeningExercise, on_delete=models.CASCADE, related_name='questions')
    question_english = models.TextField()
    question_dari = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'exercises_listeningquestion'
        ordering = ['order']
    
    def __str__(self):
        return self.question_english[:50]


class ListeningOption(models.Model):
    """Options for listening questions"""
    question = models.ForeignKey(ListeningQuestion, on_delete=models.CASCADE, related_name='options')
    text_english = models.CharField(max_length=500)
    text_dari = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'exercises_listeningoption'
        ordering = ['order']


class UserExerciseResponse(models.Model):
    """Track user responses to exercises"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_responses')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='user_responses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_responses')
    response_data = models.JSONField(help_text="Store user answers as JSON")
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=100)
    is_correct = models.BooleanField(default=False)
    xp_earned = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exercises_userexerciseresponse'
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} ({self.score}%)"
    
    def calculate_xp(self):
        """Calculate XP based on score"""
        percentage = (self.score / self.max_score) * 100
        if percentage >= 80:
            return self.exercise.xp_reward
        elif percentage >= 60:
            return int(self.exercise.xp_reward * 0.7)
        elif percentage >= 40:
            return int(self.exercise.xp_reward * 0.5)
        return 0
