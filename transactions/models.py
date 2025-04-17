from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('REFERRAL_BONUS', 'Referral Bonus'),
        ('SUBSCRIPTION_PAYMENT', 'Subscription Payment'),
        ('QUEUE_PAYMENT', 'Queue Payment'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"

class Withdrawal(models.Model):
    """
    Handles withdrawal requests from users.
    A 5% fee is applied to all withdrawals.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]

    WITHDRAWAL_TYPES = [
        ('SUBSCRIPTION', 'Subscription Withdrawal'),
        ('WALLET', 'Wallet Withdrawal'),
        ('REFERRAL', 'Referral Bonus Withdrawal'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    withdrawal_type = models.CharField(max_length=20, choices=WITHDRAWAL_TYPES, default='WALLET')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    withdrawal_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Optional fields for subscription withdrawals
    subscription = models.ForeignKey('subscriptions.Subscription', on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='withdrawals')
    wallet = models.ForeignKey('subscriptions.Wallet', on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='withdrawals')

    def save(self, *args, **kwargs):
        # Calculate 5% withdrawal fee if not already set
        if not self.withdrawal_fee:
            self.withdrawal_fee = self.amount * Decimal('0.05')
        super().save(*args, **kwargs)

    def approve(self):
        """
        Approve the withdrawal request
        """
        if self.status != 'PENDING':
            raise ValueError(f"Cannot approve withdrawal with status {self.status}")

        self.status = 'APPROVED'
        self.processed_at = timezone.now()
        self.save()

        # Update transaction status
        self.transaction.status = 'COMPLETED'
        self.transaction.completed_at = timezone.now()
        self.transaction.save()

        return self

    def reject(self):
        """
        Reject the withdrawal request and refund the amount
        """
        if self.status != 'PENDING':
            raise ValueError(f"Cannot reject withdrawal with status {self.status}")

        self.status = 'REJECTED'
        self.processed_at = timezone.now()
        self.save()

        # Update transaction status
        self.transaction.status = 'FAILED'
        self.transaction.completed_at = timezone.now()
        self.transaction.save()

        # Refund the amount if it's a wallet withdrawal
        if self.wallet:
            from subscriptions.models import Wallet
            self.wallet.deposit(
                amount=self.amount,
                description=f"Refund for rejected withdrawal #{self.id}"
            )

        return self

    def __str__(self):
        if self.subscription:
            return f"{self.user.username} - ${self.amount} - {self.subscription.plan.name} Withdrawal"
        return f"{self.user.username} - ${self.amount} - {self.get_withdrawal_type_display()}"
