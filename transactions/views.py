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
