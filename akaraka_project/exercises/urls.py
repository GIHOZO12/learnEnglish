from django.urls import path
from .views import (
    ExerciseListView, MCQExerciseView, MatchingExerciseView, TypingExerciseView, ListeningExerciseView
)

app_name = 'exercises'

urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercise_list'),
    path('mcq/<int:exercise_id>/lesson/<int:lesson_id>/', MCQExerciseView.as_view(), name='mcq_exercise'),
    path('matching/<int:exercise_id>/lesson/<int:lesson_id>/', MatchingExerciseView.as_view(), name='matching'),
    path('typing/<int:exercise_id>/lesson/<int:lesson_id>/', TypingExerciseView.as_view(), name='typing'),
    path('listening/<int:exercise_id>/lesson/<int:lesson_id>/', ListeningExerciseView.as_view(), name='listening'),
]
