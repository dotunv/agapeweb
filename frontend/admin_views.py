from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import User
from transactions.models import Transaction, Withdrawal
from decimal import Decimal
from .decorators import admin_required
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

def admin_login(request):
    """Admin login view."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin:dashboard')
        
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                next_url = request.GET.get('next', reverse('admin:dashboard'))
                return redirect(next_url)
            else:
                messages.error(request, 'Please enter a correct username and password for a staff account.')
        else:
            messages.error(request, 'Invalid username or password.')

    context = {
        'form': form,
        'site_header': 'AgapeThrift Administration',
        'site_title': 'AgapeThrift Admin',
    }
    return render(request, 'admin/login.html', context)

@admin_required
def admin_dashboard(request):
    """Admin dashboard view showing overview of system."""
    # Get total users count
    try:
        with open('user_count.txt', 'r') as f:
            total_users = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        total_users = User.objects.count()
        with open('user_count.txt', 'w') as f:
            f.write(str(total_users))
    
    # Get deposits and withdrawals statistics
    total_deposits = Transaction.objects.filter(transaction_type='deposit').count()
    total_deposits_amount = Transaction.objects.filter(
        transaction_type='deposit'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    total_withdrawals = Withdrawal.objects.count()
    total_withdrawals_amount = Withdrawal.objects.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Calculate net revenue (deposits - withdrawals)
    net_revenue = total_deposits_amount - total_withdrawals_amount
    
    # Get recent activities
    recent_activities = []
    
    # Add recent deposits
    recent_deposits = Transaction.objects.filter(
        transaction_type='deposit'
    ).order_by('-created_at')[:5]
    for deposit in recent_deposits:
        recent_activities.append({
            'type': 'deposit',
            'user': deposit.user.username,
            'action': 'made a deposit',
            'amount': deposit.amount,
            'timestamp': deposit.created_at
        })
    
    # Add recent withdrawals
    recent_withdrawals = Withdrawal.objects.order_by('-created_at')[:5]
    for withdrawal in recent_withdrawals:
        recent_activities.append({
            'type': 'withdrawal',
            'user': withdrawal.user.username,
            'action': 'requested withdrawal',
            'amount': withdrawal.amount,
            'timestamp': withdrawal.created_at
        })
    
    # Sort combined activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:5]
    
    # Get quick stats
    today = timezone.now()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    
    new_users_count = User.objects.filter(
        date_joined__gte=start_of_day
    ).count()
    
    active_users_count = User.objects.filter(
        last_login__gte=start_of_day
    ).count()
    
    pending_withdrawals = Withdrawal.objects.filter(
        status='pending'
    ).count()
    
    context = {
        'total_users': total_users,
        'total_deposits': total_deposits,
        'total_deposits_amount': total_deposits_amount,
        'total_withdrawals': total_withdrawals,
        'total_withdrawals_amount': total_withdrawals_amount,
        'net_revenue': net_revenue,
        'recent_activities': recent_activities,
        'new_users_count': new_users_count,
        'active_users_count': active_users_count,
        'pending_withdrawals': pending_withdrawals,
    }
    return render(request, 'admin/dashboard.html', context)

@admin_required
def manage_users(request):
    """View for managing users."""
    users = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin/manage_users.html', context)

@admin_required
def manage_withdrawals(request):
    """View for managing withdrawal requests."""
    withdrawals = Withdrawal.objects.all().order_by('-created_at')
    paginator = Paginator(withdrawals, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin/manage_withdrawals.html', context)

@admin_required
def manage_deposits(request):
    """View for managing deposits."""
    deposits = Transaction.objects.filter(transaction_type='deposit').order_by('-created_at')
    paginator = Paginator(deposits, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin/manage_deposits.html', context)

@admin_required
def user_balance(request, user_id):
    """View for managing user balance."""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        amount = Decimal(request.POST.get('amount', '0'))
        
        if action == 'add':
            user.balance += amount
            Transaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='admin_deposit',
                status='completed',
                description='Admin deposit'
            )
            messages.success(request, f'Added ${amount} to {user.username}\'s balance')
        elif action == 'remove':
            if user.balance >= amount:
                user.balance -= amount
                Transaction.objects.create(
                    user=user,
                    amount=amount,
                    transaction_type='admin_withdrawal',
                    status='completed',
                    description='Admin withdrawal'
                )
                messages.success(request, f'Removed ${amount} from {user.username}\'s balance')
            else:
                messages.error(request, 'Insufficient balance')
        
        user.save()
        return redirect('admin:user_balance', user_id=user.id)
    
    context = {
        'user': user,
    }
    return render(request, 'admin/user_balance.html', context)

@admin_required
def process_withdrawal(request, withdrawal_id):
    """View for processing withdrawal requests."""
    withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            withdrawal.status = 'approved'
            withdrawal.save()
            messages.success(request, f'Withdrawal request for ${withdrawal.amount} has been approved')
        elif action == 'reject':
            withdrawal.status = 'rejected'
            withdrawal.user.balance += withdrawal.amount  # Refund the amount
            withdrawal.user.save()
            withdrawal.save()
            messages.success(request, f'Withdrawal request for ${withdrawal.amount} has been rejected and refunded')
        
        return redirect('admin:manage_withdrawals')
    
    context = {
        'withdrawal': withdrawal,
    }
    return render(request, 'admin/process_withdrawal.html', context) 