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
    
    class Meta:
        model = Withdrawal
        fields = ('id', 'user', 'username', 'amount', 'status', 'transaction',
                 'transaction_details', 'withdrawal_fee', 'created_at', 'processed_at')
        read_only_fields = ('status', 'withdrawal_fee', 'processed_at') 