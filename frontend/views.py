from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from users.models import User
from subscriptions.models import Subscription, Plan
from transactions.models import Transaction

def home(request):
    """Home page view."""
    return render(request, 'home.html')

def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        referral_code = request.POST.get('referral_code')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'registration/register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'registration/register.html')
            
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        if referral_code:
            # Handle referral code logic here
            pass
            
        # Authenticate the user with the correct backend
        user = authenticate(
            request,
            username=username,
            password=password,
            backend='django.contrib.auth.backends.ModelBackend'
        )
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('frontend:dashboard')
        else:
            messages.error(request, 'Authentication failed.')
            return render(request, 'registration/register.html')
        
    return render(request, 'registration/register.html')

@login_required
def dashboard(request):
    """User dashboard view."""
    context = {
        'balance': request.user.balance,
        'recent_subscriptions': Subscription.objects.filter(user=request.user).order_by('-joined_at')[:5],
        'available_plans': Plan.objects.all(),
        'unread_notifications_count': request.user.notifications.filter(read=False).count()
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def fund_account(request):
    """Fund account view."""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # Handle payment processing here
        messages.success(request, f'Successfully funded account with ${amount}')
        return redirect('frontend:dashboard')
    return render(request, 'dashboard/fund_account.html')

@login_required
def plans(request):
    """Available plans view."""
    context = {
        'plans': Plan.objects.all()
    }
    return render(request, 'dashboard/plans.html', context)

@login_required
def subscriptions(request):
    """User subscriptions view."""
    context = {
        'subscriptions': Subscription.objects.filter(user=request.user).order_by('-created_at')
    }
    return render(request, 'dashboard/subscriptions.html', context)

@login_required
def referrals(request):
    """User referrals view."""
    context = {
        'referral_code': request.user.referral_code,
        'referrals': request.user.referrals.all()
    }
    return render(request, 'dashboard/referrals.html', context)

@login_required
def notifications(request):
    """User notifications view."""
    notifications = request.user.notifications.all()
    # Mark notifications as read
    notifications.update(read=True)
    context = {
        'notifications': notifications
    }
    return render(request, 'dashboard/notifications.html', context)

@login_required
def withdrawal(request):
    """Withdrawal view."""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # Handle withdrawal processing here
        messages.success(request, f'Successfully initiated withdrawal of ${amount}')
        return redirect('frontend:dashboard')
    return render(request, 'dashboard/withdrawal.html', context)

@login_required
def profile(request):
    """User profile view."""
    edit_mode = request.GET.get('edit') == 'true'
    
    if request.method == 'POST':
        user = request.user
        
        # Update basic fields
        user.first_name = request.POST.get('full_name', user.first_name)
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone', user.phone_number)
        
        # Handle image upload
        if 'image' in request.FILES:
            image = request.FILES['image']
            # Validate image
            if image.content_type.startswith('image/'):
                # Delete old image if it exists
                if user.profile_picture:
                    user.profile_picture.delete(save=False)
                user.profile_picture = image
            else:
                messages.error(request, 'Please upload a valid image file.')
                return render(request, 'dashboard/profile.html', {
                    'edit': True,
                    'error': 'Invalid file type. Please upload an image.'
                })
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('frontend:profile')
        except Exception as e:
            messages.error(request, 'An error occurred while updating your profile.')
            return render(request, 'dashboard/profile.html', {
                'edit': True,
                'error': str(e)
            })
            
    return render(request, 'dashboard/profile.html', {
        'edit': edit_mode,
    })

def about(request):
    """About page view."""
    return render(request, 'about.html')

def features(request):
    """Features page view."""
    return render(request, 'features.html')

def contact(request):
    """Contact page view."""
    if request.method == 'POST':
        # Handle contact form submission here
        messages.success(request, 'Message sent successfully!')
        return redirect('contact')
    return render(request, 'contact.html')

def privacy(request):
    """Privacy policy view."""
    return render(request, 'privacy.html')

def terms(request):
    """Terms and conditions view."""
    return render(request, 'terms.html')

def how_it_works(request):
    """How it works view."""
    return render(request, 'how_it_works.html')
