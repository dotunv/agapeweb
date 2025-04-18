from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from django.db.models import F, Max
from django.db import transaction
import uuid
from typing import Optional, Union, List, Dict, Any, Tuple

User = get_user_model()

class Plan(models.Model):
    """
    Represents a subscription plan in the system.

    Each plan has a type, contribution amount, and various deduction rates.
    Plans can be organized in a hierarchy with a next_plan relationship.
    """
    PLAN_TYPES = [
        ('PRE_STARTER', 'Pre-Starter Plan'),
        ('STARTER', 'Starter Plan'),
        ('BASIC_1', 'Basic 1'),
        ('BASIC_2', 'Basic 2'),
        ('STANDARD', 'Standard'),
        ('ULTIMATE_1', 'Ultimate 1'),
        ('ULTIMATE_2', 'Ultimate 2'),
    ]

    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                            help_text="Amount user contributes to join this plan")
    total_received = models.DecimalField(max_digits=10, decimal_places=2, 
                                       help_text="Total amount received from members")
    max_members = models.IntegerField(help_text="Number of members needed to complete the queue (8 or 13)")
    deduction_repurchase = models.DecimalField(max_digits=10, decimal_places=2, 
                                             help_text="Amount deducted for repurchase (1/13 of contribution)")
    deduction_maintenance = models.DecimalField(max_digits=10, decimal_places=2, 
                                              help_text="Amount deducted for maintenance (2/13 of contribution)")
    withdrawable_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                            help_text="Amount available for withdrawal after deductions")
    next_plan = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='previous_plans', 
                                help_text="Next plan to upgrade to (if applicable)")

    def __str__(self) -> str:
        """
        Return a string representation of the plan.

        Returns:
            str: The plan name and contribution amount
        """
        return f"{self.name} (${self.contribution_amount})"

    class Meta:
        """
        Meta options for the Plan model.
        """
        ordering = ['contribution_amount']

class Subscription(models.Model):
    """
    Represents a user's subscription to a plan.

    Tracks the status, queue position, and financial details of a subscription.
    Subscriptions move through a queue system where position #1 receives payments
    from other members.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    queue_position = models.IntegerField(null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_for_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        """
        Meta options for the Subscription model.
        """
        ordering = ['queue_position']

    def __str__(self) -> str:
        """
        Return a string representation of the subscription.

        Returns:
            str: The username and plan name
        """
        return f"{self.user.username} - {self.plan.name}"

    def process_payment(self, from_subscription: 'Subscription', amount: Decimal) -> 'Contribution':
        """
        Process a payment from another subscription to this one.

        This method handles the logic for processing a payment from one subscription to another,
        including updating the total received, handling queue position changes, and potentially
        triggering an upgrade to the next plan.

        Args:
            from_subscription: The subscription making the payment
            amount: The amount being paid

        Returns:
            Contribution: The created contribution record

        Raises:
            ValueError: If the subscription status is not 'ACTIVE' or if the subscription is not in a queue
        """
        if self.status != 'ACTIVE':
            raise ValueError(f"Cannot process payment for subscription with status {self.status}")

        with transaction.atomic():
            # Create contribution record
            contribution = Contribution.objects.create(
                from_subscription=from_subscription,
                to_subscription=self,
                amount=amount
            )

            # Update total received
            self.total_received = F('total_received') + amount

            # Get queue entry
            try:
                queue_entry = self.queue_entry
            except Queue.DoesNotExist:
                raise ValueError("Subscription is not in a queue")

            # If this subscription is at position #1, process the payment
            if queue_entry.position == 1:
                # Increment payments received
                queue_entry.payments_received = F('payments_received') + 1
                queue_entry.save()
                queue_entry.refresh_from_db()

                # Check if all payments have been received
                if queue_entry.payments_received >= self.plan.max_members:
                    # Calculate deductions
                    repurchase_deduction = self.plan.deduction_repurchase
                    maintenance_deduction = self.plan.deduction_maintenance

                    # Calculate available for withdrawal
                    self.available_for_withdrawal = F('available_for_withdrawal') + (
                        amount - repurchase_deduction - maintenance_deduction
                    )

                    # Process repurchase (auto-upgrade to next plan if available)
                    if self.plan.next_plan:
                        # Create a new subscription for the next plan
                        next_subscription = Subscription.objects.create(
                            user=self.user,
                            plan=self.plan.next_plan,
                            status='PENDING'
                        )

                        # Add to queue
                        Queue.add_to_queue(next_subscription)

                        # Create wallet for this plan if it doesn't exist
                        Wallet.get_or_create_wallet(
                            user=self.user,
                            wallet_type='PLAN',
                            plan=self.plan.next_plan
                        )

                    # Shift the queue (remove this subscription from position #1)
                    queue_entry.shift_queue()

            self.save()

            return contribution

    def request_withdrawal(self, amount: Decimal) -> 'Withdrawal':
        """
        Request a withdrawal from this subscription.

        This method handles the logic for requesting a withdrawal from a subscription,
        including validating the amount, updating the available_for_withdrawal balance,
        and creating the necessary transaction and withdrawal records.

        Args:
            amount: The amount to withdraw

        Returns:
            Withdrawal: The created withdrawal record

        Raises:
            ValueError: If the subscription status is not 'ACTIVE', if the amount is greater
                       than the available amount, or if the amount is not positive
        """
        if self.status != 'ACTIVE':
            raise ValueError(f"Cannot withdraw from subscription with status {self.status}")

        if amount > self.available_for_withdrawal:
            raise ValueError(f"Cannot withdraw more than available amount: ${self.available_for_withdrawal}")

        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        with transaction.atomic():
            # Update available for withdrawal
            self.available_for_withdrawal = F('available_for_withdrawal') - amount
            self.save()
            self.refresh_from_db()

            # Create transaction record
            from transactions.models import Transaction, Withdrawal
            transaction_id = f"WD-{uuid.uuid4().hex[:8]}"

            transaction_obj = Transaction.objects.create(
                user=self.user,
                transaction_type='WITHDRAWAL',
                amount=amount,
                status='PENDING',
                transaction_id=transaction_id,
                description=f"Withdrawal from {self.plan.name} subscription"
            )

            # Create withdrawal record
            withdrawal = Withdrawal.objects.create(
                user=self.user,
                amount=amount,
                status='PENDING',
                transaction=transaction_obj,
                withdrawal_type='SUBSCRIPTION',
                subscription=self
            )

            return withdrawal

class Contribution(models.Model):
    """
    Represents a payment contribution from one subscription to another.

    Tracks the source and destination subscriptions, amount, and timestamp of the contribution.
    """
    from_subscription = models.ForeignKey(Subscription, related_name='contributions_made', on_delete=models.CASCADE)
    to_subscription = models.ForeignKey(Subscription, related_name='contributions_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Return a string representation of the contribution.

        Returns:
            str: The amount, source username, and destination username
        """
        return f"${self.amount} from {self.from_subscription.user.username} to {self.to_subscription.user.username}"

class Queue(models.Model):
    """
    Manages the queue system for each plan.
    Position #1 receives payments from the next X members (8 for Pre-Starter/Starter, 13 for others).
    After receiving payments, position #1 exits and everyone shifts up.
    """
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='queues')
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE, related_name='queue_entry')
    position = models.PositiveIntegerField()
    payments_received = models.PositiveIntegerField(default=0, 
                                                  help_text="Number of payments received while at position #1")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['plan', 'position']
        unique_together = [['plan', 'position']]

    def __str__(self) -> str:
        """
        Return a string representation of the queue entry.

        Returns:
            str: The plan name, position number, and username
        """
        return f"{self.plan.name} - Position #{self.position} - {self.subscription.user.username}"

    def shift_queue(self) -> bool:
        """
        Remove position #1 and shift everyone up.

        This method is called when position #1 has received all required payments.
        It marks the subscription as completed, removes the queue entry at position #1,
        and shifts all other queue entries up by one position.

        Returns:
            bool: True if the queue was successfully shifted

        Raises:
            ValueError: If the queue entry is not at position #1
        """
        if self.position != 1:
            raise ValueError("Only position #1 can trigger a queue shift")

        with transaction.atomic():
            # Mark the subscription as completed
            self.subscription.status = 'COMPLETED'
            self.subscription.completed_at = timezone.now()
            self.subscription.save()

            # Delete this queue entry
            self_id = self.id
            self.delete()

            # Shift everyone else up
            Queue.objects.filter(plan=self.plan).update(position=F('position') - 1)

            return True

    @classmethod
    def add_to_queue(cls, subscription: Subscription) -> 'Queue':
        """
        Add a subscription to the end of its plan's queue.

        This method creates a new queue entry for the subscription at the end of its plan's queue,
        and updates the subscription's queue_position field.

        Args:
            subscription: The subscription to add to the queue

        Returns:
            Queue: The created queue entry
        """
        with transaction.atomic():
            # Find the highest position in this plan's queue
            max_position = Queue.objects.filter(plan=subscription.plan).aggregate(
                max_pos=Max('position'))['max_pos'] or 0

            # Create a new queue entry at the next position
            queue_entry = cls.objects.create(
                plan=subscription.plan,
                subscription=subscription,
                position=max_position + 1
            )

            # Update the subscription's queue position
            subscription.queue_position = max_position + 1
            subscription.save(update_fields=['queue_position'])

            return queue_entry

class Wallet(models.Model):
    """
    Manages different types of wallets for users.

    There are three types of wallets:
    - Plan-specific wallets (linked to a specific subscription plan)
    - Funding wallet (for general funds)
    - Referral wallet (for referral bonuses)

    Each wallet tracks its balance and provides methods for deposits and withdrawals.
    """
    WALLET_TYPES = [
        ('PLAN', 'Plan Wallet'),
        ('FUNDING', 'Funding Wallet'),
        ('REFERRAL', 'Referral Wallet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPES)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True,
                           help_text="Only applicable for PLAN wallet type")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'wallet_type', 'plan']]

    def __str__(self) -> str:
        """
        Return a string representation of the wallet.

        Returns:
            str: The username, wallet type (with plan name for PLAN wallets), and balance
        """
        if self.wallet_type == 'PLAN' and self.plan:
            return f"{self.user.username} - {self.plan.name} Wallet - ${self.balance}"
        return f"{self.user.username} - {self.get_wallet_type_display()} - ${self.balance}"

    @classmethod
    def get_or_create_wallet(cls, user: User, wallet_type: str, plan: Optional['Plan'] = None) -> 'Wallet':
        """
        Get or create a wallet for a user.

        This method retrieves an existing wallet or creates a new one if it doesn't exist.
        For PLAN wallet types, a plan must be specified.

        Args:
            user: The user who owns the wallet
            wallet_type: The type of wallet ('PLAN', 'FUNDING', or 'REFERRAL')
            plan: The plan associated with the wallet (required for PLAN wallet type)

        Returns:
            Wallet: The retrieved or created wallet

        Raises:
            ValueError: If wallet_type is 'PLAN' and no plan is provided
        """
        if wallet_type == 'PLAN' and not plan:
            raise ValueError("Plan is required for PLAN wallet type")

        wallet, created = cls.objects.get_or_create(
            user=user,
            wallet_type=wallet_type,
            plan=plan,
            defaults={'balance': 0}
        )
        return wallet

    def deposit(self, amount: Decimal, description: str = "Deposit") -> Decimal:
        """
        Add funds to the wallet and create a transaction record.

        This method increases the wallet balance by the specified amount and creates
        a transaction record to track the deposit.

        Args:
            amount: The amount to deposit (must be positive)
            description: A description of the deposit transaction

        Returns:
            Decimal: The new wallet balance after the deposit

        Raises:
            ValueError: If the amount is not positive
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        with transaction.atomic():
            self.balance = F('balance') + amount
            self.save()
            self.refresh_from_db()

            # Create transaction record
            from transactions.models import Transaction
            transaction_id = f"DEP-{uuid.uuid4().hex[:8]}"

            Transaction.objects.create(
                user=self.user,
                transaction_type='DEPOSIT',
                amount=amount,
                status='COMPLETED',
                transaction_id=transaction_id,
                description=description,
                completed_at=timezone.now()
            )

            return self.balance

    def withdraw(self, amount: Decimal, description: str = "Withdrawal") -> 'Withdrawal':
        """
        Withdraw funds from the wallet and create a transaction record.

        This method decreases the wallet balance by the specified amount and creates
        transaction and withdrawal records to track the withdrawal.

        Args:
            amount: The amount to withdraw (must be positive and not exceed the balance)
            description: A description of the withdrawal transaction

        Returns:
            Withdrawal: The created withdrawal record

        Raises:
            ValueError: If the amount is not positive or exceeds the available balance
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self.balance:
            raise ValueError(f"Insufficient funds. Available: ${self.balance}")

        with transaction.atomic():
            self.balance = F('balance') - amount
            self.save()
            self.refresh_from_db()

            # Create transaction and withdrawal records
            from transactions.models import Transaction, Withdrawal
            transaction_id = f"WD-{uuid.uuid4().hex[:8]}"

            transaction_obj = Transaction.objects.create(
                user=self.user,
                transaction_type='WITHDRAWAL',
                amount=amount,
                status='PENDING',
                transaction_id=transaction_id,
                description=description
            )

            withdrawal = Withdrawal.objects.create(
                user=self.user,
                amount=amount,
                status='PENDING',
                transaction=transaction_obj
            )

            return withdrawal

class Referral(models.Model):
    """
    Tracks referral relationships and bonuses.

    This model records when a user is referred by another user and manages the
    referral bonus system. When a user subscribes to a plan, their referrer
    receives a 5% bonus of the subscription amount.

    The bonus is automatically added to the referrer's referral wallet.
    """
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_record')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True,
                                   help_text="Subscription that triggered this referral bonus")
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta options for the Referral model.
        """
        unique_together = [['referrer', 'referred_user', 'subscription']]

    def __str__(self) -> str:
        """
        Return a string representation of the referral.

        Returns:
            str: The referrer username, referred user username, and bonus amount
        """
        return f"{self.referrer.username} referred {self.referred_user.username} - ${self.bonus_amount} bonus"

    @classmethod
    def create_referral_bonus(cls, subscription: Subscription) -> Optional['Referral']:
        """
        Create a referral bonus when a user subscribes to a plan.

        This method calculates a 5% bonus based on the subscription plan's contribution amount,
        creates a referral record, adds the bonus to the referrer's referral wallet, and
        creates a transaction record for the bonus.

        Args:
            subscription: The subscription that triggered the referral bonus

        Returns:
            Optional[Referral]: The created referral record, or None if the user has no referrer
        """
        user = subscription.user
        referrer = user.referred_by

        if not referrer:
            return None

        # Calculate 5% bonus
        bonus_amount = subscription.plan.contribution_amount * Decimal('0.05')

        with transaction.atomic():
            # Create referral record
            referral = cls.objects.create(
                referrer=referrer,
                referred_user=user,
                subscription=subscription,
                bonus_amount=bonus_amount
            )

            # Add bonus to referrer's referral wallet
            referral_wallet = Wallet.get_or_create_wallet(
                user=referrer,
                wallet_type='REFERRAL'
            )

            referral_wallet.deposit(
                amount=bonus_amount,
                description=f"Referral bonus from {user.username}'s {subscription.plan.name} subscription"
            )

            # Create transaction record
            from transactions.models import Transaction
            transaction_id = f"REF-{uuid.uuid4().hex[:8]}"

            Transaction.objects.create(
                user=referrer,
                transaction_type='REFERRAL_BONUS',
                amount=bonus_amount,
                status='COMPLETED',
                transaction_id=transaction_id,
                description=f"Referral bonus from {user.username}'s {subscription.plan.name} subscription",
                completed_at=timezone.now()
            )

            return referral

# Withdrawal model is now in transactions app
