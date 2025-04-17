from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid

class User(AbstractUser):
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
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    # Google OAuth fields
    google_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    profile_picture = models.URLField(max_length=500, null=True, blank=True)

    # Wallets for different subscription plans
    pre_starter_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    starter_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    basic1_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    basic2_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    standard_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ultimate1_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ultimate2_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Referral bonus wallet
    referral_bonus_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Funding wallet
    funding_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
