from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """Decorator to check if user is admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('users:home')
        return view_func(request, *args, **kwargs)
    return wrapper
