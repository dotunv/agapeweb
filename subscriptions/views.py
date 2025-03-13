from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import SubscriptionPlan, Subscription, Payment, QueuePosition
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer,
    PaymentSerializer, QueuePositionSerializer
)

# Create your views here.

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            subscription = serializer.save(user=self.request.user)
            # Create queue position
            last_position = QueuePosition.objects.filter(
                subscription__plan=subscription.plan
            ).order_by('-position').first()
            
            new_position = QueuePosition.objects.create(
                subscription=subscription,
                position=(last_position.position + 1) if last_position else 1
            )
            subscription.queue_position = new_position
            subscription.save()

    @action(detail=True, methods=['post'])
    def make_payment(self, request, pk=None):
        subscription = self.get_object()
        amount = subscription.plan.amount
        
        with transaction.atomic():
            # Create payment record
            payment = Payment.objects.create(
                subscription=subscription,
                amount=amount,
                transaction_id=f"PAY-{timezone.now().timestamp()}"
            )
            
            # Create transaction record
            from transactions.models import Transaction
            Transaction.objects.create(
                user=request.user,
                transaction_type='SUBSCRIPTION_PAYMENT',
                amount=amount,
                transaction_id=payment.transaction_id,
                description=f"Payment for {subscription.plan.name} subscription"
            )
            
            return Response(PaymentSerializer(payment).data)

    @action(detail=False, methods=['get'])
    def queue_status(self, request):
        plan_id = request.query_params.get('plan')
        if not plan_id:
            return Response(
                {"error": "Plan ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        queue = QueuePosition.objects.filter(
            subscription__plan_id=plan_id
        ).order_by('position')
        
        serializer = QueuePositionSerializer(queue, many=True)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(subscription__user=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff members can approve payments"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        payment = self.get_object()
        payment.status = 'APPROVED'
        payment.approved_at = timezone.now()
        payment.save()
        
        # Update subscription status
        subscription = payment.subscription
        subscription.status = 'ACTIVE'
        subscription.save()
        
        return Response(PaymentSerializer(payment).data)
