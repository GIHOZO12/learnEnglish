from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
import json
from .models import (
    Exercise, ExerciseLesson, MCQQuestion, MCQOption, MatchingExercise,
    TypingExercise, ListeningExercise, UserExerciseResponse
)
from courses.models import Lesson, LessonProgress


class ExerciseListView(ListView):
    """Browse all exercises"""
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Exercise.objects.filter(is_published=True)
        
        # Filter by type
        exercise_type = self.request.GET.get('type')
        if exercise_type:
            queryset = queryset.filter(exercise_type=exercise_type)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercise_type'] = self.request.GET.get('type', '')
        return context


class ExerciseBaseView(LoginRequiredMixin, View):
    """Base view for exercises"""
    
    def get_exercise(self, exercise_id):
        return get_object_or_404(Exercise, id=exercise_id, is_published=True)
    
    def record_response(self, user, exercise, lesson, response_data, score):
        """Record user's exercise response"""
        is_correct = score >= 80
        response = UserExerciseResponse.objects.create(
            user=user,
            exercise=exercise,
            lesson=lesson,
            response_data=response_data,
            score=score,
            max_score=100,
            is_correct=is_correct,
        )
        response.xp_earned = response.calculate_xp()
        response.save()
        
        # Add XP to user
        user.add_xp(response.xp_earned)
        
        return response


class MCQExerciseView(ExerciseBaseView):
    """MCQ Exercise view"""
    def get(self, request, exercise_id, lesson_id):
        exercise = self.get_exercise(exercise_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if exercise.exercise_type != 'mcq':
            messages.error(request, 'Invalid exercise type.')
            return redirect('courses:lesson_detail', course_slug=lesson.course.slug, lesson_slug=lesson.slug)
        
        questions = exercise.mcq_questions.all().prefetch_related('options')
        
        context = {
            'exercise': exercise,
            'lesson': lesson,
            'course': lesson.course,
            'questions': questions,
        }
        return render(request, 'exercises/mcq_exercise.html', context)
    
    @method_decorator(require_POST)
    def post(self, request, exercise_id, lesson_id):
        exercise = self.get_exercise(exercise_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if exercise.exercise_type != 'mcq':
            return JsonResponse({'error': 'Invalid exercise type'}, status=400)
        
        try:
            # Get responses from form data or JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                responses = data.get('responses', {})
            else:
                responses = {}
                for key, value in request.POST.items():
                    if key.startswith('question_'):
                        question_id = key.replace('question_', '')
                        responses[question_id] = value
            
            # Grade exercise
            score = 0
            max_score = 0
            response_data = {}
            
            for question_id, selected_option_id in responses.items():
                question = exercise.mcq_questions.get(id=question_id)
                max_score += 1
                
                option = MCQOption.objects.get(id=selected_option_id)
                if option.is_correct:
                    score += 1
                
                response_data[question_id] = {
                    'selected_option': selected_option_id,
                    'correct': option.is_correct
                }
            
            # Normalize score to 0-100
            normalized_score = int((score / max_score * 100)) if max_score > 0 else 0
            
            # Record response
            response = self.record_response(
                request.user, exercise, lesson,
                response_data, normalized_score
            )
            
            return JsonResponse({
                'success': True,
                'score': response.score,
                'xp_earned': response.xp_earned,
                'is_correct': response.is_correct
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class MatchingExerciseView(ExerciseBaseView):
    """Matching Exercise view"""
    def get(self, request, exercise_id, lesson_id):
        exercise = self.get_exercise(exercise_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if exercise.exercise_type != 'matching':
            messages.error(request, 'Invalid exercise type.')
            return redirect('courses:lesson_detail', course_slug=lesson.course.slug, lesson_slug=lesson.slug)
        
        matching = exercise.matching
        pairs = matching.pairs.all()
        
        context = {
            'exercise': exercise,
            'lesson': lesson,
            'course': lesson.course,
            'matching': matching,
            'matching_pairs': pairs,
        }
        return render(request, 'exercises/matching_exercise.html', context)
    
    @method_decorator(require_POST)
    def post(self, request, exercise_id, lesson_id):
        exercise = self.get_exercise(exercise_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        try:
            # Get matches from form data or JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                matches = json.loads(data.get('matches', '[]'))
            else:
                matches = json.loads(request.POST.get('matches', '[]'))
            
            matching = exercise.matching
            pairs = list(matching.pairs.all())
            
            score = 0
            response_data = {}
            
            # Simple scoring: correct order gives points
            for idx, pair_id in enumerate(matches):
                try:
                    pair = matching.pairs.get(id=pair_id)
                    is_correct = idx == pairs.index(pair)
                    
                    if is_correct:
                        score += 1
                    
                    response_data[str(pair_id)] = {
                        'position': idx,
                        'correct': is_correct
                    }
                except:
                    continue
            
            normalized_score = int((score / len(pairs) * 100)) if len(pairs) > 0 else 0
            
            response = self.record_response(
                request.user, exercise, lesson,
                response_data, normalized_score
            )
            
            return JsonResponse({
                'success': True,
                'score': response.score,
                'xp_earned': response.xp_earned,
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class TypingExerciseView(ExerciseBaseView):
    """Typing Exercise view"""
    def get(self, request, exercise_id, lesson_id):
        exercise = self.get_exercise(exercise_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if exercise.exercise_type != 'typing':
            messages.error(request, 'Invalid exercise type.')
            return redirect('courses:lesson_detail', course_slug=lesson.course.slug, lesson_slug=lesson.slug)
        
        typing = exercise.typing
        prompts = typing.prompts.all()
        
        context = {
            'exercise': exercise,
            'lesson': lesson,
            'course': lesson.course,
            'typing': typing,
            'typing_prompts': prompts,
        }
        return render(request, 'exercises/typing_exercise.html', context)
    
    @method_decorator(require_POST)
    def post(self, request, exercise_id, lesson_id):
        exercise = self.get_exercise(exercise_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        try:
            # Get answers from form data or JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                answers = data.get('answers', {})
            else:
                answers = {}
                for key, value in request.POST.items():
                    if key.startswith('answer_'):
                        prompt_id = key.replace('answer_', '')
                        answers[prompt_id] = value
            
            typing = exercise.typing
            prompts = typing.prompts.all()
            
            score = 0
            response_data = {}
            
            for prompt_id, user_answer in answers.items():
                try:
                    prompt = typing.prompts.get(id=prompt_id)
                    is_correct = prompt.correct_answer.lower().strip() == user_answer.lower().strip()
                    
                    if is_correct:
                        score += 1
                    
                    response_data[prompt_id] = {
                        'answer': user_answer,
                        'correct': is_correct
                    }
                except:
                    continue
            
            normalized_score = int((score / len(prompts) * 100)) if len(prompts) > 0 else 0
            
            response = self.record_response(
                request.user, exercise, lesson,
                response_data, normalized_score
            )
            
            return JsonResponse({
                'success': True,
                'score': response.score,
                'xp_earned': response.xp_earned,
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class ListeningExerciseView(ExerciseBaseView):
    """Listening Exercise view"""
    def get(self, request, exercise_id, lesson_id):
        exercise = self.get_exercise(exercise_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if exercise.exercise_type != 'listening':
            messages.error(request, 'Invalid exercise type.')
            return redirect('courses:lesson_detail', course_slug=lesson.course.slug, lesson_slug=lesson.slug)
        
        # Check if listening exercise exists
        try:
            listening = ListeningExercise.objects.get(exercise=exercise)
        except ListeningExercise.DoesNotExist:
            messages.error(request, 'This listening exercise has not been configured yet. Please contact support.')
            return redirect('courses:lesson_detail', course_slug=lesson.course.slug, lesson_slug=lesson.slug)
        
        questions = listening.questions.all().prefetch_related('options')
        
        context = {
            'exercise': exercise,
            'lesson': lesson,
            'course': lesson.course,
            'listening': listening,
            'listening_questions': questions,
        }
        return render(request, 'exercises/listening_exercise.html', context)
    
    @method_decorator(require_POST)
    def post(self, request, exercise_id, lesson_id):
        exercise = self.get_exercise(exercise_id)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        try:
            # Get responses from form data or JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                responses = data.get('responses', {})
            else:
                responses = {}
                for key, value in request.POST.items():
                    if key.startswith('question_'):
                        question_id = key.replace('question_', '')
                        responses[question_id] = value
            
            listening = exercise.listening
            score = 0
            response_data = {}
            
            for question_id, selected_option_id in responses.items():
                try:
                    question = listening.questions.get(id=question_id)
                    option = question.options.get(id=selected_option_id)
                    
                    if option.is_correct:
                        score += 1
                    
                    response_data[question_id] = {
                        'selected_option': selected_option_id,
                        'correct': option.is_correct
                    }
                except:
                    continue
            
            max_questions = listening.questions.count()
            normalized_score = int((score / max_questions * 100)) if max_questions > 0 else 0
            
            response = self.record_response(
                request.user, exercise, lesson,
                response_data, normalized_score
            )
            
            return JsonResponse({
                'success': True,
                'score': response.score,
                'xp_earned': response.xp_earned,
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
