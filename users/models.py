from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator
import uuid
import random
import string
from typing import Optional, Union, List, Dict, Any
from decimal import Decimal

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.

    This model adds additional fields for the subscription management system,
    including referral codes, wallet balances, and Google OAuth integration.
    """
    # Username validator to ensure it's a single word (alphanumeric)
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]+$',
        message='Username must be a single word containing only letters and numbers.'
    )

    username = models.CharField(
        _('username'), 
        max_length=150, 
        unique=True,
        validators=[username_validator],
        help_text=_('Required. 150 characters or fewer. Single word with letters and numbers only.')
    )
    email = models.EmailField(_('email address'), unique=True)
    referral_code_validator = RegexValidator(
        regex=r'^[A-Z0-9]{10}$',
        message='Referral code must be 10 characters long and contain only uppercase letters and numbers.'
    )

    referral_code = models.CharField(
        max_length=10, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[referral_code_validator]
    )
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    # Google OAuth fields
    google_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    profile_picture = models.URLField(max_length=500, null=True, blank=True)

    # Wallets for different subscription plans
    pre_starter_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )
    starter_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )
    basic1_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )
    basic2_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )
    standard_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )
    ultimate1_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )
    ultimate2_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )

    # Referral bonus wallet
    referral_bonus_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )

    # Funding wallet
    funding_wallet = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0, message="Wallet balance cannot be negative")]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        """
        Return a string representation of the user.

        Returns:
            str: The user's email address
        """
        return self.email

    def generate_referral_code(self) -> str:
        """
        Generate a unique 10-character referral code consisting of uppercase letters and numbers.

        Returns:
            str: A unique 10-character referral code
        """
        while True:
            # Generate a random 10-character code
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

            # Check if the code is unique
            if not User.objects.filter(referral_code=code).exists():
                return code

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Override the save method to generate a referral code if one doesn't exist.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            None
        """
        # Generate a referral code if one doesn't exist
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()

        super().save(*args, **kwargs)

    @property
    def balance(self) -> float:
        """
        Calculate the total balance by summing up all wallet balances.

        Returns:
            float: The total balance across all wallets
        """
        return float(
            self.pre_starter_wallet +
            self.starter_wallet +
            self.basic1_wallet +
            self.basic2_wallet +
            self.standard_wallet +
            self.ultimate1_wallet +
            self.ultimate2_wallet +
            self.referral_bonus_wallet +
            self.funding_wallet
        )

class Notification(models.Model):
    """
    Represents a notification for a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=50, choices=[
        ('SUBSCRIPTION', 'Subscription'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSACTION', 'Transaction'),
        ('REFERRAL', 'Referral'),
        ('SYSTEM', 'System')
    ])

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.message[:50]}"
