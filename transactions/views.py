from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from .models import Transaction, Withdrawal
from .forms import WithdrawalForm
import logging
from datetime import timedelta
from django.db.models import Sum, Count
from django.contrib.auth import get_user_model

# Get a logger for this module
logger = logging.getLogger('agape.transactions')

class TransactionListView(LoginRequiredMixin, ListView):
    """View for listing user's transactions."""
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionDetailView(LoginRequiredMixin, DetailView):
    """View for showing transaction details."""
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class WithdrawalListView(LoginRequiredMixin, ListView):
    """View for listing user's withdrawals."""
    model = Withdrawal
    template_name = 'transactions/withdrawal_list.html'
    context_object_name = 'withdrawals'
    paginate_by = 20

    def get_queryset(self):
        return Withdrawal.objects.filter(user=self.request.user)

class WithdrawalCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new withdrawal request."""
    model = Withdrawal
    form_class = WithdrawalForm
    template_name = 'transactions/withdrawal_form.html'
    success_url = '/transactions/withdrawals/'

    def form_valid(self, form):
        try:
            with transaction.atomic():
                withdrawal = form.save(commit=False)
                withdrawal.user = self.request.user
                withdrawal.save()

                # Create transaction record
                Transaction.objects.create(
                    user=self.request.user,
                    transaction_type='WITHDRAWAL',
                    amount=withdrawal.amount,
                    transaction_id=f"WD-{timezone.now().timestamp()}",
                    description=f"Withdrawal request for ${withdrawal.amount}"
                )

                logger.info(
                    f"Withdrawal request created: user={self.request.user.username}, "
                    f"amount=${withdrawal.amount}, type={withdrawal.withdrawal_type}"
                )
                messages.success(self.request, 'Withdrawal request submitted successfully!')
                return super().form_valid(form)
        except Exception as e:
            logger.error(
                f"Error creating withdrawal request: user={self.request.user.username}, "
                f"error={str(e)}"
            )
            messages.error(self.request, f'Error creating withdrawal request: {str(e)}')
            return super().form_invalid(form)

@user_passes_test(lambda u: u.is_staff)
def approve_withdrawal(request, pk):
    """View for staff to approve a withdrawal request."""
    withdrawal = get_object_or_404(Withdrawal, pk=pk)

    try:
        if withdrawal.status != 'PENDING':
            messages.error(
                request,
                f"Cannot approve withdrawal with status {withdrawal.status}"
            )
            return redirect('transactions:withdrawal_detail', pk=pk)

        with transaction.atomic():
            withdrawal.status = 'APPROVED'
            withdrawal.processed_at = timezone.now()
            withdrawal.save()

            # Update transaction status
            withdrawal.transaction.status = 'COMPLETED'
            withdrawal.transaction.completed_at = timezone.now()
            withdrawal.transaction.save()

        logger.info(
            f"Withdrawal approved: id={withdrawal.id}, user={withdrawal.user.username}, "
            f"amount=${withdrawal.amount}"
        )
        messages.success(request, 'Withdrawal request approved successfully!')

    except Exception as e:
        logger.error(f"Error approving withdrawal: id={pk}, error={str(e)}")
        messages.error(request, f'Error approving withdrawal: {str(e)}')

    return redirect('transactions:withdrawal_detail', pk=pk)

@user_passes_test(lambda u: u.is_staff)
def reject_withdrawal(request, pk):
    """View for staff to reject a withdrawal request."""
    withdrawal = get_object_or_404(Withdrawal, pk=pk)

    try:
        if withdrawal.status != 'PENDING':
            messages.error(
                request,
                f"Cannot reject withdrawal with status {withdrawal.status}"
            )
            return redirect('transactions:withdrawal_detail', pk=pk)

        with transaction.atomic():
            withdrawal.status = 'REJECTED'
            withdrawal.processed_at = timezone.now()
            withdrawal.save()

            # Update transaction status
            withdrawal.transaction.status = 'FAILED'
            withdrawal.transaction.completed_at = timezone.now()
            withdrawal.transaction.save()

        logger.info(
            f"Withdrawal rejected: id={withdrawal.id}, user={withdrawal.user.username}, "
            f"amount=${withdrawal.amount}"
        )
        messages.success(request, 'Withdrawal request rejected.')

    except Exception as e:
        logger.error(f"Error rejecting withdrawal: id={pk}, error={str(e)}")
        messages.error(request, f'Error rejecting withdrawal: {str(e)}')

    return redirect('transactions:withdrawal_detail', pk=pk)

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """Admin dashboard view with time period filtering."""
    # Get time period from request (default to 'today')
    period = request.GET.get('period', 'today')
    
    # Calculate date range based on period
    now = timezone.now()
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        prev_start_date = start_date - timedelta(days=1)
    elif period == 'week':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        prev_start_date = start_date - timedelta(weeks=1)
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_start_date = (start_date - timedelta(days=1)).replace(day=1)
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        prev_start_date = start_date - timedelta(days=1)
    
    # Get total users
    User = get_user_model()
    total_users = User.objects.count()
    
    # Get total deposits
    deposits = Transaction.objects.filter(
        transaction_type='DEPOSIT',
        status='COMPLETED',
        created_at__gte=start_date
    )
    total_deposits = deposits.count()
    total_deposits_amount = deposits.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get previous period deposits
    prev_deposits = Transaction.objects.filter(
        transaction_type='DEPOSIT',
        status='COMPLETED',
        created_at__gte=prev_start_date,
        created_at__lt=start_date
    )
    prev_deposits_amount = prev_deposits.aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate deposits percentage change
    deposits_percent_change = 0
    if prev_deposits_amount > 0:
        deposits_percent_change = ((total_deposits_amount - prev_deposits_amount) / prev_deposits_amount) * 100
    
    # Get total withdrawals
    withdrawals = Transaction.objects.filter(
        transaction_type='WITHDRAWAL',
        status='COMPLETED',
        created_at__gte=start_date
    )
    total_withdrawals = withdrawals.count()
    total_withdrawals_amount = withdrawals.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get previous period withdrawals
    prev_withdrawals = Transaction.objects.filter(
        transaction_type='WITHDRAWAL',
        status='COMPLETED',
        created_at__gte=prev_start_date,
        created_at__lt=start_date
    )
    prev_withdrawals_amount = prev_withdrawals.aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate withdrawals percentage change
    withdrawals_percent_change = 0
    if prev_withdrawals_amount > 0:
        withdrawals_percent_change = ((total_withdrawals_amount - prev_withdrawals_amount) / prev_withdrawals_amount) * 100
    
    # Calculate net revenue
    net_revenue = total_deposits_amount - total_withdrawals_amount
    prev_net_revenue = prev_deposits_amount - prev_withdrawals_amount
    
    # Calculate net revenue percentage change
    net_revenue_percent_change = 0
    if prev_net_revenue > 0:
        net_revenue_percent_change = ((net_revenue - prev_net_revenue) / prev_net_revenue) * 100
    
    # Get recent activities
    recent_activities = Transaction.objects.filter(
        created_at__gte=start_date
    ).select_related('user').order_by('-created_at')[:10]
    
    # Get new users count
    new_users_count = User.objects.filter(
        date_joined__gte=start_date
    ).count()
    
    # Get previous period new users
    prev_new_users_count = User.objects.filter(
        date_joined__gte=prev_start_date,
        date_joined__lt=start_date
    ).count()
    
    # Calculate new users percentage change
    new_users_percent_change = 0
    if prev_new_users_count > 0:
        new_users_percent_change = ((new_users_count - prev_new_users_count) / prev_new_users_count) * 100
    
    # Get active users count (users with transactions in the period)
    active_users_count = User.objects.filter(
        transaction__created_at__gte=start_date
    ).distinct().count()
    
    # Get previous period active users
    prev_active_users_count = User.objects.filter(
        transaction__created_at__gte=prev_start_date,
        transaction__created_at__lt=start_date
    ).distinct().count()
    
    # Calculate active users percentage change
    active_users_percent_change = 0
    if prev_active_users_count > 0:
        active_users_percent_change = ((active_users_count - prev_active_users_count) / prev_active_users_count) * 100
    
    # Get pending withdrawals
    pending_withdrawals = Withdrawal.objects.filter(
        status='PENDING'
    ).count()
    
    # Get total transactions
    total_transactions = Transaction.objects.filter(
        created_at__gte=start_date
    ).count()
    
    # Get previous period transactions
    prev_total_transactions = Transaction.objects.filter(
        created_at__gte=prev_start_date,
        created_at__lt=start_date
    ).count()
    
    # Calculate transactions percentage change
    transactions_percent_change = 0
    if prev_total_transactions > 0:
        transactions_percent_change = ((total_transactions - prev_total_transactions) / prev_total_transactions) * 100
    
    context = {
        'total_users': total_users,
        'total_deposits': total_deposits,
        'total_deposits_amount': total_deposits_amount,
        'deposits_percent_change': deposits_percent_change,
        'total_withdrawals': total_withdrawals,
        'total_withdrawals_amount': total_withdrawals_amount,
        'withdrawals_percent_change': withdrawals_percent_change,
        'net_revenue': net_revenue,
        'recent_activities': recent_activities,
        'new_users_count': new_users_count,
        'active_users_count': active_users_count,
        'pending_withdrawals': pending_withdrawals,
        'total_transactions': total_transactions,
        'period': period,
    }
    
    return render(request, 'admin/dashboard.html', context)
