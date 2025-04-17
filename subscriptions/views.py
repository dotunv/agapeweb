from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.db.models import F
from .models import  Subscription, Plan, Contribution, Withdrawal
from .serializers import (
    PlanSerializer, SubscriptionSerializer,
    PlanSerializer, ContributionSerializer, WithdrawalSerializer
)

# Create your views here.

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Check if user already has an active subscription
        if Subscription.objects.filter(user=self.request.user, status='ACTIVE').exists():
            raise serializers.ValidationError("You already have an active subscription")
        
        subscription = serializer.save(user=self.request.user)
        # Set initial queue position
        last_position = Subscription.objects.filter(
            plan=subscription.plan,
            status__in=['PENDING', 'ACTIVE']
        ).aggregate(max_pos=models.Max('queue_position'))['max_pos'] or 0
        subscription.queue_position = last_position + 1
        subscription.save()

    @action(detail=False, methods=['get'])
    def my_subscription(self):
        subscription = get_object_or_404(Subscription, user=self.request.user, status='ACTIVE')
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def queue_position(self):
        subscription = get_object_or_404(Subscription, user=self.request.user, status='ACTIVE')
        return Response({
            'position': subscription.queue_position,
            'total_in_queue': Subscription.objects.filter(
                plan=subscription.plan,
                status__in=['PENDING', 'ACTIVE']
            ).count()
        })

# class PaymentViewSet(viewsets.ModelViewSet):
#     serializer_class = PaymentSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Payment.objects.filter(subscription__user=self.request.user)

#     @action(detail=True, methods=['post'])
#     def approve(self, request, pk=None):
#         if not request.user.is_staff:
#             return Response(
#                 {"error": "Only staff members can approve payments"},
#                 status=status.HTTP_403_FORBIDDEN
#             )
            
#         payment = self.get_object()
#         payment.status = 'APPROVED'
#         payment.approved_at = timezone.now()
#         payment.save()
        
#         # Update subscription status
#         subscription = payment.subscription
#         subscription.status = 'ACTIVE'
#         subscription.save()
        
#         return Response(PaymentSerializer(payment).data)

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class ContributionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_subscriptions = Subscription.objects.filter(user=self.request.user)
        return Contribution.objects.filter(
            models.Q(from_subscription__in=user_subscriptions) |
            models.Q(to_subscription__in=user_subscriptions)
        )

    @action(detail=False, methods=['get'])
    def received(self, request):
        user_subscriptions = Subscription.objects.filter(user=request.user)
        contributions = Contribution.objects.filter(to_subscription__in=user_subscriptions)
        serializer = self.get_serializer(contributions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def made(self, request):
        user_subscriptions = Subscription.objects.filter(user=request.user)
        contributions = Contribution.objects.filter(from_subscription__in=user_subscriptions)
        serializer = self.get_serializer(contributions, many=True)
        return Response(serializer.data)

class WithdrawalViewSet(viewsets.ModelViewSet):
    serializer_class = WithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Withdrawal.objects.filter(subscription__user=self.request.user)

    def perform_create(self, serializer):
        subscription = get_object_or_404(
            Subscription,
            user=self.request.user,
            status='ACTIVE'
        )
        
        # Validate withdrawal amount
        amount = serializer.validated_data['amount']
        if amount > subscription.available_for_withdrawal:
            raise serializers.ValidationError(
                f"Cannot withdraw more than available amount: ${subscription.available_for_withdrawal}"
            )
        
        if amount > subscription.plan.withdrawal_limit:
            raise serializers.ValidationError(
                f"Amount exceeds plan withdrawal limit of ${subscription.plan.withdrawal_limit}"
            )
        
        serializer.save(subscription=subscription)
        
        # Update available_for_withdrawal
        subscription.available_for_withdrawal = F('available_for_withdrawal') - amount
        subscription.save()
