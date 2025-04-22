from rest_framework import serializers
from .models import Plan, Subscription, Contribution, Queue, Wallet, Referral
from typing import Dict, Any, List, Optional
class PlanSerializer(serializers.ModelSerializer):
    """
    Serializer for Plan model.
    
    Includes the name of the next plan in the plan progression.
    """
    next_plan_name = serializers.CharField(
        source='next_plan.name', 
        read_only=True, 
        allow_null=True
    )

    class Meta:
        model = Plan
        fields = ['id', 'name', 'plan_type', 'contribution_amount', 'total_received', 
                 'max_members', 'deduction_repurchase', 'deduction_maintenance', 
                 'withdrawable_amount', 'next_plan', 'next_plan_name']

class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Subscription model.
    
    Includes additional fields for the plan name and username.
    """
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'plan_name', 'username', 'status', 'queue_position',
                 'joined_at', 'completed_at', 'total_received', 'available_for_withdrawal']
        extra_kwargs = {
            'status': {'read_only': True},
            'queue_position': {'read_only': True},
            'total_received': {'read_only': True},
            'available_for_withdrawal': {'read_only': True}
        }

class ContributionSerializer(serializers.ModelSerializer):
    """
    Serializer for Contribution model.
    
    Includes the usernames of both the sender and recipient.
    """
    from_user = serializers.CharField(
        source='from_subscription.user.username', 
        read_only=True
    )
    to_user = serializers.CharField(
        source='to_subscription.user.username', 
        read_only=True
    )

    class Meta:
        model = Contribution
        fields = ['id', 'from_subscription', 'to_subscription', 'from_user', 'to_user',
                 'amount', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True}
        }
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that from_subscription and to_subscription are different."""
        if attrs.get('from_subscription') == attrs.get('to_subscription'):
            raise serializers.ValidationError(
                {"from_subscription": "Cannot contribute to the same subscription."}
            )
        return attrs

class QueueSerializer(serializers.ModelSerializer):
    """
    Serializer for Queue model.
    
    Includes additional fields for plan name and username.
    """
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    username = serializers.CharField(source='subscription.user.username', read_only=True)

    class Meta:
        model = Queue
        fields = ['id', 'plan', 'plan_name', 'subscription', 'username', 'position', 
                 'payments_received', 'created_at', 'updated_at']
        extra_kwargs = {
            'position': {'read_only': True},
            'payments_received': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for Wallet model.
    
    Includes additional fields for username, plan name, and wallet type display.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True, allow_null=True)
    wallet_type_display = serializers.CharField(source='get_wallet_type_display', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'username', 'wallet_type', 'wallet_type_display', 
                 'plan', 'plan_name', 'balance', 'created_at', 'updated_at']
        extra_kwargs = {
            'balance': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

class ReferralSerializer(serializers.ModelSerializer):
    """
    Serializer for Referral model.
    
    Includes additional fields for referrer username, referred user username, and plan name.
    """
    referrer_username = serializers.CharField(source='referrer.username', read_only=True)
    referred_username = serializers.CharField(source='referred_user.username', read_only=True)
    plan_name = serializers.CharField(
        source='subscription.plan.name', 
        read_only=True, 
        allow_null=True
    )

    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referrer_username', 'referred_user', 'referred_username',
                 'subscription', 'plan_name', 'bonus_amount', 'created_at']
        extra_kwargs = {
            'bonus_amount': {'read_only': True},
            'created_at': {'read_only': True}
        }
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that referrer and referred_user are different."""
        if attrs.get('referrer') == attrs.get('referred_user'):
            raise serializers.ValidationError(
                {"referred_user": "Cannot refer yourself."}
            )
        return attrs
