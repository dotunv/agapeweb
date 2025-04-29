from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserUpdateForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Notification

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('frontend:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'users/profile.html', context)

@login_required
def referrals(request):
    referrals = User.objects.filter(referred_by=request.user)
    context = {
        'referrals': referrals,
        'referral_count': referrals.count()
    }
    return render(request, 'users/referrals.html', context)

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_profile'

    def get_object(self):
        return self.request.user

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    """Delete a notification."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(["POST"])
def mark_all_read(request):
    """Mark all notifications as read."""
    request.user.notifications.filter(read=False).update(read=True)
    return JsonResponse({'status': 'success'})

# Example of creating a notification
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

@require_POST
@login_required
def create_notification(request):
    """Create a notification for the authenticated user."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'info')
        if not message:
            return JsonResponse({'status': 'error', 'message': 'Message is required.'}, status=400)
        notification = Notification.create_notification(
            user=request.user,
            title=title,
            message=message,
            notification_type=notification_type
        )
        return JsonResponse({
            'status': 'success',
            'notification': {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.isoformat()
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# (keep the test view as well)
def create_test_notification(request):
    """Create a test notification (for development only)."""
    if request.user.is_authenticated:
        notification = Notification.create_notification(
            user=request.user,
            title="Test Notification",
            message="This is a test notification message.",
            notification_type='info'
        )
        return JsonResponse({
            'status': 'success',
            'notification': {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.isoformat()
            }
        })
    return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
