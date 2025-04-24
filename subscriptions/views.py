from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.db import transaction as db_transaction
from django.utils import timezone
from django.db.models import F, Q, Max
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import (
    Subscription, Plan, Contribution, Queue, Wallet, Referral
)
from .forms import SubscriptionForm
import logging
from typing import Dict, Any

# Get a logger for this module
logger = logging.getLogger('agape.subscriptions')

User = get_user_model()

class PlanListView(LoginRequiredMixin, ListView):
    model = Plan
    template_name = 'subscriptions/plan_list.html'
    context_object_name = 'plans'

class PlanDetailView(LoginRequiredMixin, DetailView):
    model = Plan
    template_name = 'subscriptions/plan_detail.html'
    context_object_name = 'plan'

@login_required
def subscribe(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            try:
                # Check if user already has an active subscription
                if Subscription.objects.filter(user=request.user, status='ACTIVE').exists():
                    messages.error(request, "You already have an active subscription")
                    return redirect('subscriptions:plan_list')

                with db_transaction.atomic():
                    subscription = form.save(commit=False)
                    subscription.user = request.user
                    subscription.plan = plan
                    subscription.status = 'PENDING'
                    subscription.save()

                    # Add to queue
                    Queue.add_to_queue(subscription)

                    # Create wallet for this plan if it doesn't exist
                    Wallet.get_or_create_wallet(
                        user=request.user,
                        wallet_type='PLAN',
                        plan=plan
                    )

                    # Process referral if applicable
                    if request.user.referred_by:
                        Referral.create_referral_bonus(subscription)

                    messages.success(request, f"Successfully subscribed to {plan.name} plan!")
                    return redirect('subscriptions:my_subscription')
            except Exception as e:
                logger.error(f"Error creating subscription: {str(e)}")
                messages.error(request, "An error occurred while processing your subscription")
                return redirect('subscriptions:plan_list')
    else:
        form = SubscriptionForm()

    return render(request, 'subscriptions/subscribe.html', {
        'form': form,
        'plan': plan
    })

@login_required
def my_subscription(request):
    subscription = get_object_or_404(Subscription, user=request.user, status='ACTIVE')

    try:
        queue_entry = Queue.objects.get(subscription=subscription)
        total_in_queue = Queue.objects.filter(plan=subscription.plan).count()
        queue_info = {
            'position': queue_entry.position,
            'total_in_queue': total_in_queue,
            'payments_received': queue_entry.payments_received if queue_entry.position == 1 else 0,
            'max_payments': subscription.plan.max_members
        }
    except Queue.DoesNotExist:
        queue_info = None

    context = {
        'subscription': subscription,
        'queue_info': queue_info
    }
    return render(request, 'subscriptions/my_subscription.html', context)

@login_required
def queue_status(request):
    """Get all queue positions for all plans"""
    queues = Queue.objects.all().select_related('plan', 'subscription__user')

    # Group by plan
    result = {}
    for queue in queues:
        plan_name = queue.plan.name
        if plan_name not in result:
            result[plan_name] = []

        result[plan_name].append({
            'position': queue.position,
            'username': queue.subscription.user.username,
            'joined_at': queue.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render(request, 'subscriptions/queue_status.html', {'queues': result})

class ContributionListView(LoginRequiredMixin, ListView):
    model = Contribution
    template_name = 'subscriptions/contribution_list.html'
    context_object_name = 'contributions'

    def get_queryset(self):
        user_subscriptions = Subscription.objects.filter(user=self.request.user)
        return Contribution.objects.filter(
            Q(from_subscription__in=user_subscriptions) |
            Q(to_subscription__in=user_subscriptions)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_subscriptions = Subscription.objects.filter(user=self.request.user)
        
        context['received_contributions'] = Contribution.objects.filter(
            to_subscription__in=user_subscriptions
        )
        context['made_contributions'] = Contribution.objects.filter(
            from_subscription__in=user_subscriptions
        )
        return context

@login_required
def wallet_overview(request):
    wallets = Wallet.objects.filter(user=request.user)
    
    balances = {}
    for wallet in wallets:
        key = f"{wallet.wallet_type}"
        if wallet.plan:
            key += f"_{wallet.plan.name}"
        balances[key] = {
            'balance': wallet.balance,
            'total_received': wallet.total_received,
            'total_withdrawn': wallet.total_withdrawn,
            'last_transaction': wallet.last_transaction_at
        }

    return render(request, 'subscriptions/wallet_overview.html', {
        'wallets': wallets,
        'balances': balances
    })

@login_required
def referral_overview(request):
    # Get referrals made by this user
    referrals = Referral.objects.filter(referrer=request.user).select_related('referred')
    
    # Calculate statistics
    total_referrals = referrals.count()
    active_referrals = referrals.filter(status='ACTIVE').count()
    total_earnings = sum(ref.amount for ref in referrals if ref.status == 'PAID')
    
    context = {
        'referrals': referrals,
        'stats': {
            'total_referrals': total_referrals,
            'active_referrals': active_referrals,
            'total_earnings': total_earnings
        }
    }
    return render(request, 'subscriptions/referral_overview.html', context)
