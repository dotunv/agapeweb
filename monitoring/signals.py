from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription, Payment
from .metrics import (
    user_registrations_total,
    subscription_creations_total,
    payment_attempts_total,
    payment_amount_total,
)

User = get_user_model()

@receiver(post_save, sender=User)
def track_user_registration(sender, instance, created, **kwargs):
    if created:
        user_registrations_total.inc()

@receiver(post_save, sender=Subscription)
def track_subscription_creation(sender, instance, created, **kwargs):
    if created:
        subscription_creations_total.labels(
            plan_type=instance.plan.name
        ).inc()

@receiver(post_save, sender=Payment)
def track_payment(sender, instance, created, **kwargs):
    if created:
        payment_attempts_total.labels(
            status=instance.status
        ).inc()
        
        if instance.status == 'completed':
            payment_amount_total.labels(
                currency=instance.currency
            ).inc(instance.amount) 