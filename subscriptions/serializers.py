from rest_framework import serializers
from .models import Plan, Subscription, Contribution, Queue, Wallet, Referral

class PlanSerializer(serializers.ModelSerializer):
    next_plan_name = serializers.CharField(source='next_plan.name', read_only=True, allow_null=True)

    class Meta:
        model = Plan
        fields = ['id', 'name', 'plan_type', 'contribution_amount', 'total_received', 
                 'max_members', 'deduction_repurchase', 'deduction_maintenance', 
                 'withdrawable_amount', 'next_plan', 'next_plan_name']

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

class QueueSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    username = serializers.CharField(source='subscription.user.username', read_only=True)

    class Meta:
        model = Queue
        fields = ['id', 'plan', 'plan_name', 'subscription', 'username', 'position', 
                 'payments_received', 'created_at', 'updated_at']
        read_only_fields = ['position', 'payments_received', 'created_at', 'updated_at']

class WalletSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True, allow_null=True)
    wallet_type_display = serializers.CharField(source='get_wallet_type_display', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'username', 'wallet_type', 'wallet_type_display', 
                 'plan', 'plan_name', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['balance', 'created_at', 'updated_at']

class ReferralSerializer(serializers.ModelSerializer):
    referrer_username = serializers.CharField(source='referrer.username', read_only=True)
    referred_username = serializers.CharField(source='referred_user.username', read_only=True)
    plan_name = serializers.CharField(source='subscription.plan.name', read_only=True, allow_null=True)

    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referrer_username', 'referred_user', 'referred_username',
                 'subscription', 'plan_name', 'bonus_amount', 'created_at']
        read_only_fields = ['bonus_amount', 'created_at']
