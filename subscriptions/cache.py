"""
Caching module for the subscriptions app.

This module provides functions for caching and retrieving frequently accessed data,
such as subscription plans, queue positions, and wallet balances.
"""

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from typing import List, Dict, Any, Optional, Union
from decimal import Decimal
import logging

from .models import Plan, Queue, Wallet, Subscription, Referral

logger = logging.getLogger(__name__)

# Cache keys
PLANS_CACHE_KEY = 'subscription_plans'
PLAN_CACHE_KEY_TEMPLATE = 'subscription_plan_{}'
QUEUE_POSITIONS_CACHE_KEY_TEMPLATE = 'queue_positions_{}'
WALLET_BALANCE_CACHE_KEY_TEMPLATE = 'wallet_balance_{}_{}'
USER_SUBSCRIPTIONS_CACHE_KEY_TEMPLATE = 'user_subscriptions_{}'

# Cache timeouts (in seconds)
PLANS_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours
QUEUE_CACHE_TIMEOUT = 60 * 5  # 5 minutes
WALLET_CACHE_TIMEOUT = 60 * 5  # 5 minutes
SUBSCRIPTION_CACHE_TIMEOUT = 60 * 15  # 15 minutes


def get_all_plans() -> List[Dict[str, Any]]:
    """
    Get all subscription plans from cache or database.
    
    Returns:
        List[Dict[str, Any]]: List of plans as dictionaries
    """
    # Try to get plans from cache
    plans = cache.get(PLANS_CACHE_KEY)
    
    if plans is None:
        logger.debug("Plans cache miss, fetching from database")
        # Cache miss, get from database
        plans_queryset = Plan.objects.all().order_by('price')
        
        # Convert to list of dictionaries for serialization
        plans = [
            {
                'id': plan.id,
                'name': plan.name,
                'price': float(plan.price),
                'queue_size': plan.queue_size,
                'repurchase_percentage': float(plan.repurchase_percentage),
                'maintenance_percentage': float(plan.maintenance_percentage),
                'created_at': plan.created_at.isoformat() if plan.created_at else None,
            }
            for plan in plans_queryset
        ]
        
        # Cache the plans
        cache.set(PLANS_CACHE_KEY, plans, PLANS_CACHE_TIMEOUT)
    else:
        logger.debug("Plans cache hit")
    
    return plans


def get_plan(plan_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific subscription plan from cache or database.
    
    Args:
        plan_id (int): The ID of the plan to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: The plan as a dictionary, or None if not found
    """
    cache_key = PLAN_CACHE_KEY_TEMPLATE.format(plan_id)
    
    # Try to get plan from cache
    plan = cache.get(cache_key)
    
    if plan is None:
        logger.debug(f"Plan {plan_id} cache miss, fetching from database")
        # Cache miss, get from database
        try:
            plan_obj = Plan.objects.get(id=plan_id)
            
            # Convert to dictionary for serialization
            plan = {
                'id': plan_obj.id,
                'name': plan_obj.name,
                'price': float(plan_obj.price),
                'queue_size': plan_obj.queue_size,
                'repurchase_percentage': float(plan_obj.repurchase_percentage),
                'maintenance_percentage': float(plan_obj.maintenance_percentage),
                'created_at': plan_obj.created_at.isoformat() if plan_obj.created_at else None,
            }
            
            # Cache the plan
            cache.set(cache_key, plan, PLANS_CACHE_TIMEOUT)
        except Plan.DoesNotExist:
            logger.warning(f"Plan with ID {plan_id} not found")
            return None
    else:
        logger.debug(f"Plan {plan_id} cache hit")
    
    return plan


def get_queue_positions(plan_id: int) -> List[Dict[str, Any]]:
    """
    Get queue positions for a specific plan from cache or database.
    
    Args:
        plan_id (int): The ID of the plan to get queue positions for
        
    Returns:
        List[Dict[str, Any]]: List of queue positions as dictionaries
    """
    cache_key = QUEUE_POSITIONS_CACHE_KEY_TEMPLATE.format(plan_id)
    
    # Try to get queue positions from cache
    positions = cache.get(cache_key)
    
    if positions is None:
        logger.debug(f"Queue positions for plan {plan_id} cache miss, fetching from database")
        # Cache miss, get from database
        queue_queryset = Queue.objects.filter(plan_id=plan_id).order_by('position')
        
        # Convert to list of dictionaries for serialization
        positions = [
            {
                'id': queue.id,
                'position': queue.position,
                'subscription_id': queue.subscription_id,
                'user_id': queue.subscription.user_id if queue.subscription else None,
                'username': queue.subscription.user.username if queue.subscription and queue.subscription.user else None,
                'created_at': queue.created_at.isoformat() if queue.created_at else None,
            }
            for queue in queue_queryset
        ]
        
        # Cache the queue positions
        cache.set(cache_key, positions, QUEUE_CACHE_TIMEOUT)
    else:
        logger.debug(f"Queue positions for plan {plan_id} cache hit")
    
    return positions


def get_wallet_balance(user_id: int, wallet_type: str, plan_id: Optional[int] = None) -> Optional[Decimal]:
    """
    Get wallet balance from cache or database.
    
    Args:
        user_id (int): The ID of the user
        wallet_type (str): The type of wallet (PLAN, FUNDING, REFERRAL)
        plan_id (Optional[int]): The ID of the plan (required for PLAN wallet type)
        
    Returns:
        Optional[Decimal]: The wallet balance, or None if not found
    """
    cache_key = WALLET_BALANCE_CACHE_KEY_TEMPLATE.format(user_id, f"{wallet_type}_{plan_id}" if plan_id else wallet_type)
    
    # Try to get wallet balance from cache
    balance = cache.get(cache_key)
    
    if balance is None:
        logger.debug(f"Wallet balance for user {user_id}, type {wallet_type}, plan {plan_id} cache miss, fetching from database")
        # Cache miss, get from database
        try:
            wallet_queryset = Wallet.objects.filter(user_id=user_id, wallet_type=wallet_type)
            
            if plan_id and wallet_type == 'PLAN':
                wallet_queryset = wallet_queryset.filter(plan_id=plan_id)
            
            wallet = wallet_queryset.first()
            
            if wallet:
                balance = wallet.balance
                # Cache the balance
                cache.set(cache_key, balance, WALLET_CACHE_TIMEOUT)
            else:
                logger.warning(f"Wallet not found for user {user_id}, type {wallet_type}, plan {plan_id}")
                return Decimal('0.00')
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return Decimal('0.00')
    else:
        logger.debug(f"Wallet balance for user {user_id}, type {wallet_type}, plan {plan_id} cache hit")
    
    return balance


def get_user_subscriptions(user_id: int) -> List[Dict[str, Any]]:
    """
    Get user subscriptions from cache or database.
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        List[Dict[str, Any]]: List of subscriptions as dictionaries
    """
    cache_key = USER_SUBSCRIPTIONS_CACHE_KEY_TEMPLATE.format(user_id)
    
    # Try to get subscriptions from cache
    subscriptions = cache.get(cache_key)
    
    if subscriptions is None:
        logger.debug(f"Subscriptions for user {user_id} cache miss, fetching from database")
        # Cache miss, get from database
        subscription_queryset = Subscription.objects.filter(user_id=user_id)
        
        # Convert to list of dictionaries for serialization
        subscriptions = [
            {
                'id': sub.id,
                'plan_id': sub.plan_id,
                'plan_name': sub.plan.name if sub.plan else None,
                'status': sub.status,
                'created_at': sub.created_at.isoformat() if sub.created_at else None,
                'approved_at': sub.approved_at.isoformat() if sub.approved_at else None,
                'completed_at': sub.completed_at.isoformat() if sub.completed_at else None,
            }
            for sub in subscription_queryset
        ]
        
        # Cache the subscriptions
        cache.set(cache_key, subscriptions, SUBSCRIPTION_CACHE_TIMEOUT)
    else:
        logger.debug(f"Subscriptions for user {user_id} cache hit")
    
    return subscriptions


def invalidate_plans_cache():
    """Invalidate the plans cache."""
    logger.debug("Invalidating plans cache")
    cache.delete(PLANS_CACHE_KEY)
    
    # Also invalidate individual plan caches
    for plan in Plan.objects.all():
        cache.delete(PLAN_CACHE_KEY_TEMPLATE.format(plan.id))


def invalidate_queue_cache(plan_id: int):
    """
    Invalidate the queue cache for a specific plan.
    
    Args:
        plan_id (int): The ID of the plan
    """
    logger.debug(f"Invalidating queue cache for plan {plan_id}")
    cache.delete(QUEUE_POSITIONS_CACHE_KEY_TEMPLATE.format(plan_id))


def invalidate_wallet_cache(user_id: int, wallet_type: str, plan_id: Optional[int] = None):
    """
    Invalidate the wallet cache for a specific user and wallet type.
    
    Args:
        user_id (int): The ID of the user
        wallet_type (str): The type of wallet (PLAN, FUNDING, REFERRAL)
        plan_id (Optional[int]): The ID of the plan (required for PLAN wallet type)
    """
    logger.debug(f"Invalidating wallet cache for user {user_id}, type {wallet_type}, plan {plan_id}")
    cache_key = WALLET_BALANCE_CACHE_KEY_TEMPLATE.format(user_id, f"{wallet_type}_{plan_id}" if plan_id else wallet_type)
    cache.delete(cache_key)


def invalidate_subscription_cache(user_id: int):
    """
    Invalidate the subscription cache for a specific user.
    
    Args:
        user_id (int): The ID of the user
    """
    logger.debug(f"Invalidating subscription cache for user {user_id}")
    cache.delete(USER_SUBSCRIPTIONS_CACHE_KEY_TEMPLATE.format(user_id))


# Signal handlers to automatically invalidate cache when models change

@receiver(post_save, sender=Plan)
def invalidate_plan_cache_on_save(sender, instance, **kwargs):
    """Invalidate plan cache when a plan is saved."""
    invalidate_plans_cache()


@receiver(post_delete, sender=Plan)
def invalidate_plan_cache_on_delete(sender, instance, **kwargs):
    """Invalidate plan cache when a plan is deleted."""
    invalidate_plans_cache()


@receiver(post_save, sender=Queue)
def invalidate_queue_cache_on_save(sender, instance, **kwargs):
    """Invalidate queue cache when a queue entry is saved."""
    if instance.plan_id:
        invalidate_queue_cache(instance.plan_id)


@receiver(post_delete, sender=Queue)
def invalidate_queue_cache_on_delete(sender, instance, **kwargs):
    """Invalidate queue cache when a queue entry is deleted."""
    if instance.plan_id:
        invalidate_queue_cache(instance.plan_id)


@receiver(post_save, sender=Wallet)
def invalidate_wallet_cache_on_save(sender, instance, **kwargs):
    """Invalidate wallet cache when a wallet is saved."""
    invalidate_wallet_cache(instance.user_id, instance.wallet_type, instance.plan_id if instance.wallet_type == 'PLAN' else None)


@receiver(post_delete, sender=Wallet)
def invalidate_wallet_cache_on_delete(sender, instance, **kwargs):
    """Invalidate wallet cache when a wallet is deleted."""
    invalidate_wallet_cache(instance.user_id, instance.wallet_type, instance.plan_id if instance.wallet_type == 'PLAN' else None)


@receiver(post_save, sender=Subscription)
def invalidate_subscription_cache_on_save(sender, instance, **kwargs):
    """Invalidate subscription cache when a subscription is saved."""
    invalidate_subscription_cache(instance.user_id)
    
    # Also invalidate queue cache if the subscription is in a queue
    if instance.plan_id:
        invalidate_queue_cache(instance.plan_id)


@receiver(post_delete, sender=Subscription)
def invalidate_subscription_cache_on_delete(sender, instance, **kwargs):
    """Invalidate subscription cache when a subscription is deleted."""
    invalidate_subscription_cache(instance.user_id)
    
    # Also invalidate queue cache if the subscription was in a queue
    if instance.plan_id:
        invalidate_queue_cache(instance.plan_id)