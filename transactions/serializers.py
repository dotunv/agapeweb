from rest_framework import serializers
from .models import Transaction, Withdrawal

class TransactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'username', 'transaction_type', 'amount',
                 'status', 'transaction_id', 'description', 'created_at', 'completed_at')
        read_only_fields = ('status', 'completed_at')

class WithdrawalSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    transaction_details = TransactionSerializer(source='transaction', read_only=True)
    withdrawal_type_display = serializers.CharField(source='get_withdrawal_type_display', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True, allow_null=True)
    wallet_type = serializers.CharField(source='wallet.get_wallet_type_display', read_only=True, allow_null=True)

    class Meta:
        model = Withdrawal
        fields = ('id', 'user', 'username', 'amount', 'status', 'withdrawal_type', 
                 'withdrawal_type_display', 'transaction', 'transaction_details', 
                 'withdrawal_fee', 'created_at', 'processed_at', 'subscription', 
                 'subscription_plan', 'wallet', 'wallet_type')
        read_only_fields = ('status', 'withdrawal_fee', 'processed_at')
