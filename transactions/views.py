from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Transaction, Withdrawal
from .serializers import TransactionSerializer, WithdrawalSerializer

# Create your views here.

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class WithdrawalViewSet(viewsets.ModelViewSet):
    serializer_class = WithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Withdrawal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            withdrawal = serializer.save(user=self.request.user)
            
            # Create transaction record
            Transaction.objects.create(
                user=self.request.user,
                transaction_type='WITHDRAWAL',
                amount=withdrawal.amount,
                transaction_id=f"WD-{timezone.now().timestamp()}",
                description=f"Withdrawal request for ${withdrawal.amount}"
            )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff members can approve withdrawals"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        withdrawal = self.get_object()
        withdrawal.status = 'APPROVED'
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        # Update transaction status
        withdrawal.transaction.status = 'COMPLETED'
        withdrawal.transaction.completed_at = timezone.now()
        withdrawal.transaction.save()
        
        return Response(WithdrawalSerializer(withdrawal).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff members can reject withdrawals"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        withdrawal = self.get_object()
        withdrawal.status = 'REJECTED'
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        # Update transaction status
        withdrawal.transaction.status = 'FAILED'
        withdrawal.transaction.completed_at = timezone.now()
        withdrawal.transaction.save()
        
        return Response(WithdrawalSerializer(withdrawal).data)
