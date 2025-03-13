from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, Payment, QueuePosition

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class QueuePositionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='subscription.user.username', read_only=True)
    
    class Meta:
        model = QueuePosition
        fields = ('id', 'position', 'payments_received', 'username', 'created_at', 'updated_at')

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_amount = serializers.DecimalField(source='plan.amount', max_digits=10, decimal_places=2, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    queue_position = QueuePositionSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ('id', 'user', 'username', 'plan', 'plan_name', 'plan_amount',
                 'status', 'queue_position', 'created_at', 'updated_at')
        read_only_fields = ('status', 'queue_position')

class PaymentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='subscription.user.username', read_only=True)
    plan_name = serializers.CharField(source='subscription.plan.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ('id', 'subscription', 'username', 'plan_name', 'amount',
                 'status', 'transaction_id', 'created_at', 'approved_at')
        read_only_fields = ('status', 'approved_at') 