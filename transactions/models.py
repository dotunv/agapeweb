from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
from typing import Optional, Union, List, Dict, Any, Tuple

class Transaction(models.Model):
    """
    Represents a financial transaction in the system.

    This model tracks all financial transactions, including deposits, withdrawals,
    referral bonuses, and subscription payments. Each transaction has a type,
    amount, status, and associated user.
    """
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

    def __str__(self) -> str:
        """
        Return a string representation of the transaction.

        Returns:
            str: The username, transaction type, and amount
        """
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"

class Withdrawal(models.Model):
    """
    Represents a withdrawal request in the system.

    This model tracks withdrawal requests, including the amount, status,
    and associated transaction. Each withdrawal has a type, fee, and
    associated wallet.
    """
    WITHDRAWAL_TYPES = [
        ('WALLET', 'Wallet Withdrawal'),
        ('REFERRAL', 'Referral Withdrawal'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    withdrawal_type = models.CharField(max_length=20, choices=WITHDRAWAL_TYPES)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    withdrawal_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wallet = models.ForeignKey('subscriptions.Wallet', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        """
        Return a string representation of the withdrawal.

        Returns:
            str: The username, amount, and withdrawal type
        """
        return f"{self.user.username} - ${self.amount} - {self.get_withdrawal_type_display()}"
