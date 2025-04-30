from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('admin:login')}?next={request.path}")
        if not request.user.is_staff:
            return redirect('frontend:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view 