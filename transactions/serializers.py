from rest_framework import serializers
from .models import Transaction, Withdrawal
from typing import Dict, Any, List, Optional, Union

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.

    This serializer handles the conversion of Transaction model instances to JSON
    and vice versa. It includes a derived field for the username of the user who
    created the transaction.
    """
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        """
        Meta class for TransactionSerializer.

        Defines the model, fields, and read-only fields for the serializer.
        """
        model = Transaction
        fields = ('id', 'user', 'username', 'transaction_type', 'amount',
                 'status', 'transaction_id', 'description', 'created_at', 'completed_at')
        read_only_fields = ('status', 'completed_at')

class WithdrawalSerializer(serializers.ModelSerializer):
    """
    Serializer for Withdrawal model.

    This serializer handles the conversion of Withdrawal model instances to JSON
    and vice versa. It includes several derived fields for related objects and
    display values.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    transaction_details = TransactionSerializer(source='transaction', read_only=True)
    withdrawal_type_display = serializers.CharField(source='get_withdrawal_type_display', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True, allow_null=True)
    wallet_type = serializers.CharField(source='wallet.get_wallet_type_display', read_only=True, allow_null=True)

    class Meta:
        """
        Meta class for WithdrawalSerializer.

        Defines the model, fields, and read-only fields for the serializer.
        """
        model = Withdrawal
        fields = ('id', 'user', 'username', 'amount', 'status', 'withdrawal_type', 
                 'withdrawal_type_display', 'transaction', 'transaction_details', 
                 'withdrawal_fee', 'created_at', 'processed_at', 'subscription', 
                 'subscription_plan', 'wallet', 'wallet_type')
        read_only_fields = ('status', 'withdrawal_fee', 'processed_at')
