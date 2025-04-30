from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import User
from transactions.models import Transaction, Withdrawal
from decimal import Decimal
from .decorators import admin_required
from django.conf import settings

@admin_required
def admin_dashboard(request):
    """Admin dashboard view showing overview of system."""
    if request.method == 'POST':
        try:
            new_user_count = int(request.POST.get('total_users', 0))
            if new_user_count < 0:
                messages.error(request, 'User count cannot be negative')
            else:
                # Store the user count in settings or cache
                with open('user_count.txt', 'w') as f:
                    f.write(str(new_user_count))
                messages.success(request, f'Total users updated to {new_user_count}')
                return redirect('admin:dashboard')
        except ValueError:
            messages.error(request, 'Please enter a valid number')
    
    try:
        with open('user_count.txt', 'r') as f:
            total_users = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        total_users = 10  # Default value
        with open('user_count.txt', 'w') as f:
            f.write(str(total_users))
    
    # Get all users for the table
    users = User.objects.all().order_by('-date_joined')
    
    # Get statistics
    total_withdrawals = Withdrawal.objects.count()
    total_deposits = Transaction.objects.filter(transaction_type='deposit').count()
    
    context = {
        'total_users': total_users,
        'total_withdrawals': total_withdrawals,
        'total_deposits': total_deposits,
        'users': users,  # Add users to the context
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