from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    username = models.CharField(_('username'), max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    # Wallets for different subscription plans
    basic1_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    basic2_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    standard_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ultimate1_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ultimate2_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Referral bonus wallet
    referral_bonus_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Funding wallet
    funding_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
