from django.db import models
from django.conf import settings
from decimal import Decimal

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('BASIC1', 'Basic 1'),
        ('BASIC2', 'Basic 2'),
        ('STANDARD', 'Standard'),
        ('ULTIMATE1', 'Ultimate 1'),
        ('ULTIMATE2', 'Ultimate 2'),
    ]
    
    name = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.get_name_display()} - ${self.amount}"

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    queue_position = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'plan']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.subscription.user.username} - {self.amount}"

class QueuePosition(models.Model):
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE)
    position = models.IntegerField()
    payments_received = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subscription.user.username} - Position {self.position}"
