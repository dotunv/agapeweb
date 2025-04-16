from rest_framework import serializers
from .models import Plan, Subscription, Contribution, Withdrawal

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'plan_type', 'price', 'max_members', 'maintenance_fee', 
                 'repurchase_amount', 'withdrawal_limit']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'plan_name', 'username', 'status', 'queue_position',
                 'joined_at', 'completed_at', 'total_received', 'available_for_withdrawal']
        read_only_fields = ['status', 'queue_position', 'total_received', 'available_for_withdrawal']

class ContributionSerializer(serializers.ModelSerializer):
    from_user = serializers.CharField(source='from_subscription.user.username', read_only=True)
    to_user = serializers.CharField(source='to_subscription.user.username', read_only=True)

    class Meta:
        model = Contribution
        fields = ['id', 'from_subscription', 'to_subscription', 'from_user', 'to_user',
                 'amount', 'created_at']
        read_only_fields = ['created_at']

class WithdrawalSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='subscription.user.username', read_only=True)

    class Meta:
        model = Withdrawal
        fields = ['id', 'subscription', 'username', 'amount', 'status', 
                 'requested_at', 'completed_at']
        read_only_fields = ['status', 'completed_at'] 