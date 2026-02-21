from django.shortcuts import render, redirect
from django.views.generic import View, ListView, DetailView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm
from gamification.models import Badge, UserBadge
from courses.models import LessonProgress
from datetime import datetime


class HomeView(View):
    """Landing/Home page"""
    def get(self, request):
        context = {
            'total_users': CustomUser.objects.count(),
            'total_lessons': 0,  # Will be updated when Lesson model is created
        }
        return render(request, 'users/home.html', context)


class RegisterView(View):
    """User registration"""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('courses:dashboard')
        form = CustomUserCreationForm()
        return render(request, 'users/register.html', {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('users:login')
        return render(request, 'users/register.html', {'form': form})


class LoginView(View):
    """User login"""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('courses:dashboard')
        form = CustomAuthenticationForm()
        return render(request, 'users/login.html', {'form': form})
    
    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                user.update_last_activity()
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('courses:dashboard')
        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    """User logout"""
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('users:home')


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """User profile page"""
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        username = self.kwargs.get('username')
        return CustomUser.objects.get(username=username)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['badges'] = UserBadge.objects.filter(user=user)
        context['lessons_completed'] = LessonProgress.objects.filter(
            user=user, 
            is_completed=True
        ).count()
        context['is_own_profile'] = user == self.request.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update user profile"""
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'username': self.request.user.username})
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class LeaderboardView(ListView):
    """Global leaderboard"""
    model = CustomUser
    template_name = 'users/leaderboard.html'
    context_object_name = 'users'
    paginate_by = 50
    
    def get_queryset(self):
        return CustomUser.objects.filter(is_active=True).order_by('-total_xp')[:100]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            rank = list(CustomUser.objects.filter(
                is_active=True,
                total_xp__gt=self.request.user.total_xp
            ).values_list('id', flat=True)).count() + 1
            context['user_rank'] = rank
        return context


class StreakLeaderboardView(ListView):
    """Streak leaderboard"""
    model = CustomUser
    template_name = 'users/streak_leaderboard.html'
    context_object_name = 'users'
    paginate_by = 50
    
    def get_queryset(self):
        return CustomUser.objects.filter(is_active=True).order_by('-current_streak')[:100]
