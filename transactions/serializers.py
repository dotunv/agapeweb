from rest_framework import serializers
from .models import Transaction, Withdrawal
from typing import Dict, Any, List, Optional, Union, TypedDict
from django.db import models
class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.

    This serializer handles the conversion of Transaction model instances to JSON
    and vice versa. It includes a derived field for the username of the user who
    created the transaction.

    Fields:
        username: Derived field showing the username of the transaction creator
        id: The transaction's unique identifier
        user: The user who created the transaction
        transaction_type: The type of transaction
        amount: The monetary amount for the transaction
        status: The current status of the transaction (read-only)
        transaction_id: External transaction identifier
        description: Text description of the transaction
        created_at: When the transaction was created
        completed_at: When the transaction was completed (read-only)
    """
    username = serializers.CharField(
        source='user.username', 
        read_only=True,
        help_text="Username of the transaction creator"
    )

    class Meta:
        """
        Meta class for TransactionSerializer.

        Defines the model, fields, and field-specific settings for the serializer.
        """
        model = Transaction
        fields = ('id', 'user', 'username', 'transaction_type', 'amount',
                 'status', 'transaction_id', 'description', 'created_at', 'completed_at')
        extra_kwargs = {
            'status': {'read_only': True},
            'completed_at': {'read_only': True}
        }
        
    def validate_amount(self, value: float) -> float:
        """
        Validate that the transaction amount is positive.
        
        Args:
            value: The amount to validate
            
        Returns:
            The validated amount
            
        Raises:
            ValidationError: If amount is not positive
        """
        if value <= 0:
            raise serializers.ValidationError("Transaction amount must be positive.")
        return value

class WithdrawalSerializer(serializers.ModelSerializer):
    """
    Serializer for Withdrawal model.

    This serializer handles the conversion of Withdrawal model instances to JSON
    and vice versa. It includes several derived fields for related objects and
    display values.

    Fields:
        username: The username of the user making the withdrawal
        transaction_details: Nested serializer with full transaction details
        withdrawal_type_display: Human-readable withdrawal type
        subscription_plan: Name of the plan associated with this withdrawal
        wallet_type: Human-readable wallet type
        id: The withdrawal's unique identifier
        user: Reference to the user making the withdrawal
        amount: The withdrawal amount
        status: Current status of withdrawal (read-only)
        withdrawal_type: Type of withdrawal being made
        transaction: Reference to associated transaction
        withdrawal_fee: Calculated fee for this withdrawal (read-only)
        created_at: When the withdrawal was created
        processed_at: When the withdrawal was processed (read-only)
        subscription: Associated subscription reference
        wallet: Associated wallet reference
    """
    username = serializers.CharField(
        source='user.username', 
        read_only=True,
        help_text="Username of the user making the withdrawal"
    )
    transaction_details = TransactionSerializer(
        source='transaction', 
        read_only=True,
        help_text="Detailed information about the associated transaction"
    )
    withdrawal_type_display = serializers.CharField(
        source='get_withdrawal_type_display', 
        read_only=True,
        help_text="Human-readable withdrawal type"
    )
    subscription_plan = serializers.CharField(
        source='subscription.plan.name', 
        read_only=True, 
        allow_null=True,
        help_text="Name of associated subscription plan, if any"
    )
    wallet_type = serializers.CharField(
        source='wallet.get_wallet_type_display', 
        read_only=True, 
        allow_null=True,
        help_text="Human-readable wallet type, if applicable"
    )

    class Meta:
        """
        Meta class for WithdrawalSerializer.

        Defines the model, fields, and field-specific settings for the serializer.
        """
        model = Withdrawal
        fields = ('id', 'user', 'username', 'amount', 'status', 'withdrawal_type', 
                 'withdrawal_type_display', 'transaction', 'transaction_details', 
                 'withdrawal_fee', 'created_at', 'processed_at', 'subscription', 
                 'subscription_plan', 'wallet', 'wallet_type')
        extra_kwargs = {
            'status': {'read_only': True},
            'withdrawal_fee': {'read_only': True},
            'processed_at': {'read_only': True}
        }
        
    def validate_amount(self, value: float) -> float:
        """
        Validate that the withdrawal amount is positive.
        
        Args:
            value: The amount to validate
            
        Returns:
            The validated amount
            
        Raises:
            ValidationError: If amount is not positive
        """
        if value <= 0:
            raise serializers.ValidationError("Withdrawal amount must be positive.")
        return value
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the complete withdrawal request.
        
        Ensures either a subscription or wallet is provided, but not both.
        
        Args:
            attrs: The attribute dictionary to validate
            
        Returns:
            The validated attributes
            
        Raises:
            ValidationError: If validation fails
        """
        subscription = attrs.get('subscription')
        wallet = attrs.get('wallet')
        
        # Check that either subscription or wallet is provided, but not both
        if subscription and wallet:
            raise serializers.ValidationError(
                {"non_field_errors": "Cannot specify both subscription and wallet."}
            )
        elif not subscription and not wallet:
            raise serializers.ValidationError(
                {"non_field_errors": "Must specify either subscription or wallet."}
            )
            
        return attrs
