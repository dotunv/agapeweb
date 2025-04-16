from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Plan(models.Model):
    PLAN_TYPES = [
        ('PRE_STARTER', 'Pre-Starter Plan'),
        ('STARTER', 'Starter Plan'),
        ('BASIC_1', 'Basic 1'),
        ('BASIC_2', 'Basic 2'),
        ('STANDARD', 'Standard'),
        ('ULTIMATE_1', 'Ultimate 1'),
        ('ULTIMATE_2', 'Ultimate 2'),
    ]

    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_members = models.IntegerField()
    maintenance_fee = models.DecimalField(max_digits=10, decimal_places=2)
    repurchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    withdrawal_limit = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} (${self.price})"

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    queue_position = models.IntegerField(null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_for_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['queue_position']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

class Contribution(models.Model):
    from_subscription = models.ForeignKey(Subscription, related_name='contributions_made', on_delete=models.CASCADE)
    to_subscription = models.ForeignKey(Subscription, related_name='contributions_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"${self.amount} from {self.from_subscription.user.username} to {self.to_subscription.user.username}"

class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"${self.amount} - {self.subscription.user.username}"
