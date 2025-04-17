from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction as db_transaction
from django.utils import timezone
from django.db.models import F, Q, Max
from .models import (
    Subscription, Plan, Contribution, Queue, Wallet, Referral
)
from .serializers import (
    PlanSerializer, SubscriptionSerializer, ContributionSerializer,
    QueueSerializer, WalletSerializer, ReferralSerializer
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

        with db_transaction.atomic():
            subscription = serializer.save(user=self.request.user, status='PENDING')

            # Add to queue
            Queue.add_to_queue(subscription)

            # Create wallet for this plan if it doesn't exist
            Wallet.get_or_create_wallet(
                user=self.request.user,
                wallet_type='PLAN',
                plan=subscription.plan
            )

            # Process referral if applicable
            if self.request.user.referred_by:
                Referral.create_referral_bonus(subscription)

    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        subscription = get_object_or_404(Subscription, user=request.user, status='ACTIVE')
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def queue_position(self, request):
        subscription = get_object_or_404(Subscription, user=request.user, status='ACTIVE')

        try:
            queue_entry = Queue.objects.get(subscription=subscription)
            total_in_queue = Queue.objects.filter(plan=subscription.plan).count()

            return Response({
                'position': queue_entry.position,
                'total_in_queue': total_in_queue,
                'payments_received': queue_entry.payments_received if queue_entry.position == 1 else 0,
                'max_payments': subscription.plan.max_members
            })
        except Queue.DoesNotExist:
            return Response({
                'error': 'Subscription is not in a queue'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def all_queues(self, request):
        """
        Get all queue positions for all plans (public endpoint)
        """
        queues = Queue.objects.all().select_related('plan', 'subscription__user')

        # Group by plan
        result = {}
        for queue in queues:
            plan_name = queue.plan.name
            if plan_name not in result:
                result[plan_name] = []

            result[plan_name].append({
                'position': queue.position,
                'username': queue.subscription.user.username,
                'joined_at': queue.created_at
            })

        return Response(result)

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

# PlanViewSet is now consolidated with SubscriptionPlanViewSet

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

class QueueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Queue.objects.all().select_related('plan', 'subscription__user')

    @action(detail=False, methods=['get'])
    def my_position(self, request):
        """
        Get the user's position in all queues they are in
        """
        user_subscriptions = Subscription.objects.filter(user=request.user)
        queues = Queue.objects.filter(subscription__in=user_subscriptions).select_related('plan')

        result = []
        for queue in queues:
            result.append({
                'plan': queue.plan.name,
                'position': queue.position,
                'payments_received': queue.payments_received if queue.position == 1 else 0,
                'max_payments': queue.plan.max_members,
                'created_at': queue.created_at
            })

        return Response(result)

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def balances(self, request):
        """
        Get all wallet balances for the user
        """
        wallets = self.get_queryset().select_related('plan')

        result = {
            'total_balance': 0,
            'wallets': []
        }

        for wallet in wallets:
            wallet_info = {
                'id': wallet.id,
                'type': wallet.get_wallet_type_display(),
                'balance': float(wallet.balance)
            }

            if wallet.wallet_type == 'PLAN' and wallet.plan:
                wallet_info['plan'] = wallet.plan.name

            result['wallets'].append(wallet_info)
            result['total_balance'] += float(wallet.balance)

        return Response(result)

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        """
        Deposit funds into a wallet
        """
        wallet = self.get_object()

        try:
            amount = float(request.data.get('amount', 0))
            description = request.data.get('description', 'Deposit')

            if amount <= 0:
                return Response({
                    'error': 'Amount must be positive'
                }, status=status.HTTP_400_BAD_REQUEST)

            new_balance = wallet.deposit(amount, description)

            return Response({
                'success': True,
                'new_balance': new_balance,
                'message': f'${amount} deposited successfully'
            })
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ReferralViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Show referrals made by this user
        return Referral.objects.filter(referrer=self.request.user)

    @action(detail=False, methods=['get'])
    def my_referrals(self, request):
        """
        Get all users referred by the current user
        """
        referred_users = User.objects.filter(referred_by=request.user)

        result = []
        for user in referred_users:
            referrals = Referral.objects.filter(
                referrer=request.user,
                referred_user=user
            )

            total_bonus = sum(r.bonus_amount for r in referrals)

            result.append({
                'username': user.username,
                'email': user.email,
                'date_joined': user.date_joined,
                'total_bonus': float(total_bonus),
                'referrals_count': referrals.count()
            })

        return Response(result)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get referral statistics for the current user
        """
        referrals = self.get_queryset()
        referred_users = User.objects.filter(referred_by=request.user)

        total_bonus = sum(r.bonus_amount for r in referrals)

        return Response({
            'total_referred_users': referred_users.count(),
            'total_bonus': float(total_bonus),
            'total_referrals': referrals.count()
        })
