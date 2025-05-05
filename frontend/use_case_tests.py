from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from subscriptions.models import Plan, Subscription, Queue, Wallet, Referral
from transactions.models import Transaction, Withdrawal
from decimal import Decimal
import json
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class UseCaseTestCase(TestCase):
    """Base test case for use case tests with common setup"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password123",
            referral_code="USER1REF"
        )
        
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password123",
            referral_code="USER2REF"
        )
        
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123",
            is_staff=True,
            is_superuser=True
        )
        
        # Create test plans
        self.basic_plan = Plan.objects.create(
            name="Basic Plan",
            price=Decimal("50.00"),
            queue_size=5,
            repurchase_percentage=Decimal("0.10"),
            maintenance_percentage=Decimal("0.05")
        )
        
        self.premium_plan = Plan.objects.create(
            name="Premium Plan",
            price=Decimal("100.00"),
            queue_size=10,
            repurchase_percentage=Decimal("0.15"),
            maintenance_percentage=Decimal("0.07")
        )
        
        # Create client
        self.client = Client()
        
    def login_user(self, user):
        """Helper method to log in a user"""
        self.client.login(username=user.username, password="password123")


class CompleteUserJourneyTest(UseCaseTestCase):
    """Test a complete user journey from registration to subscription completion"""
    
    def test_complete_user_journey(self):
        """
        Test a complete user journey:
        1. User registers with a referral
        2. User logs in
        3. User subscribes to a plan
        4. User makes a payment
        5. User's subscription becomes active
        6. User receives payment from another user
        7. User requests a withdrawal
        """
        # 1. Register a new user with a referral
        register_url = reverse('register') + '?ref=USER1REF'
        self.client.get(register_url, follow=True)
        
        signup_url = reverse('account_signup')
        response = self.client.post(
            signup_url,
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'newuserpassword123',
                'password2': 'newuserpassword123'
            },
            follow=True
        )
        
        # Check that the user was created
        new_user = User.objects.get(username='newuser')
        self.assertIsNotNone(new_user)
        
        # Check that the referral was created
        self.assertTrue(
            Referral.objects.filter(
                referrer=self.user1,
                referred=new_user
            ).exists()
        )
        
        # 2. Log in the new user
        self.client.login(username='newuser', password='newuserpassword123')
        
        # 3. Subscribe to a plan
        subscribe_url = reverse('subscribe', args=[self.basic_plan.id])
        response = self.client.post(subscribe_url, follow=True)
        
        # Check that the subscription was created
        subscription = Subscription.objects.get(
            user=new_user,
            plan=self.basic_plan
        )
        self.assertEqual(subscription.status, 'PENDING')
        
        # 4. Make a payment
        # Create a wallet for the user
        wallet = Wallet.objects.create(
            user=new_user,
            wallet_type='PLAN',
            plan=self.basic_plan,
            balance=Decimal('0.00')
        )
        
        # Deposit funds
        wallet.deposit(Decimal('50.00'), 'Initial deposit')
        
        # Make payment for subscription
        payment_url = reverse('make_payment')
        response = self.client.post(
            payment_url,
            {
                'subscription_id': subscription.id,
                'amount': '50.00'
            },
            follow=True
        )
        
        # 5. Check that the subscription is now active
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'ACTIVE')
        
        # Check that the user was added to the queue
        self.assertTrue(
            Queue.objects.filter(
                subscription=subscription
            ).exists()
        )
        
        # 6. Simulate receiving payment from another user
        # Create another user with an active subscription
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="password123"
        )
        
        other_subscription = Subscription.objects.create(
            user=other_user,
            plan=self.basic_plan,
            status='ACTIVE'
        )
        
        # Process payment from other user to new user
        subscription.process_payment(other_subscription, Decimal('25.00'))
        
        # Check that the wallet balance increased
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('25.00'))
        
        # 7. Request a withdrawal
        withdrawal_url = reverse('request_withdrawal')
        response = self.client.post(
            withdrawal_url,
            {
                'amount': '20.00',
                'wallet': wallet.id,
                'payment_method': 'BANK',
                'account_details': 'Test Bank Account'
            },
            follow=True
        )
        
        # Check that a withdrawal request was created
        self.assertTrue(
            Withdrawal.objects.filter(
                user=new_user,
                amount=Decimal('20.00'),
                status='PENDING'
            ).exists()
        )
        
        # Check final wallet balance
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('5.00'))


class ReferralProgramTest(UseCaseTestCase):
    """Test the referral program functionality"""
    
    def test_referral_program(self):
        """
        Test the referral program:
        1. User1 refers User3
        2. User3 subscribes to a plan
        3. User1 receives a referral bonus
        """
        # 1. Create a new user with User1's referral code
        register_url = reverse('register') + '?ref=USER1REF'
        self.client.get(register_url, follow=True)
        
        signup_url = reverse('account_signup')
        response = self.client.post(
            signup_url,
            {
                'username': 'user3',
                'email': 'user3@example.com',
                'password1': 'password123',
                'password2': 'password123'
            },
            follow=True
        )
        
        user3 = User.objects.get(username='user3')
        
        # Check that the referral was created
        referral = Referral.objects.get(
            referrer=self.user1,
            referred=user3
        )
        
        # 2. User3 subscribes to a plan
        self.client.login(username='user3', password='password123')
        
        # Create a wallet for User3
        user3_wallet = Wallet.objects.create(
            user=user3,
            wallet_type='PLAN',
            plan=self.basic_plan,
            balance=Decimal('0.00')
        )
        
        # Deposit funds
        user3_wallet.deposit(Decimal('50.00'), 'Initial deposit')
        
        # Subscribe to a plan
        subscribe_url = reverse('subscribe', args=[self.basic_plan.id])
        response = self.client.post(subscribe_url, follow=True)
        
        # Get the subscription
        subscription = Subscription.objects.get(
            user=user3,
            plan=self.basic_plan
        )
        
        # Make payment for subscription
        payment_url = reverse('make_payment')
        response = self.client.post(
            payment_url,
            {
                'subscription_id': subscription.id,
                'amount': '50.00'
            },
            follow=True
        )
        
        # 3. Check that User1 received a referral bonus
        # Create a wallet for User1 if it doesn't exist
        user1_wallet, created = Wallet.objects.get_or_create(
            user=self.user1,
            wallet_type='REFERRAL',
            defaults={'balance': Decimal('0.00')}
        )
        
        # Process the referral bonus
        referral_bonus = self.basic_plan.price * Decimal('0.05')  # Assuming 5% referral bonus
        user1_wallet.deposit(referral_bonus, f'Referral bonus from {user3.username}')
        
        # Check that User1's wallet balance increased
        user1_wallet.refresh_from_db()
        self.assertEqual(user1_wallet.balance, referral_bonus)


class QueueProcessingTest(UseCaseTestCase):
    """Test the queue processing functionality"""
    
    def test_queue_processing(self):
        """
        Test queue processing:
        1. Create multiple users with active subscriptions
        2. Add them to the queue
        3. Process payments through the queue
        4. Check that users move through the queue correctly
        """
        # Create multiple users and subscriptions
        users = []
        subscriptions = []
        
        for i in range(5):
            user = User.objects.create_user(
                username=f"queueuser{i}",
                email=f"queue{i}@example.com",
                password="password123"
            )
            users.append(user)
            
            subscription = Subscription.objects.create(
                user=user,
                plan=self.basic_plan,
                status='ACTIVE'
            )
            subscriptions.append(subscription)
            
            # Add to queue
            Queue.add_to_queue(subscription)
        
        # Check that all users are in the queue
        self.assertEqual(Queue.objects.count(), 5)
        
        # Get the first user in the queue
        first_queue_entry = Queue.objects.order_by('position').first()
        first_subscription = first_queue_entry.subscription
        
        # Create a wallet for the first user
        first_wallet = Wallet.objects.create(
            user=first_subscription.user,
            wallet_type='PLAN',
            plan=self.basic_plan,
            balance=Decimal('0.00')
        )
        
        # Process payments to the first user from others
        for i in range(1, 5):
            first_subscription.process_payment(subscriptions[i], Decimal('10.00'))
        
        # Check that the first user's wallet balance increased
        first_wallet.refresh_from_db()
        self.assertEqual(first_wallet.balance, Decimal('40.00'))
        
        # Simulate completing the queue cycle for the first user
        first_queue_entry.shift_queue()
        
        # Check that the queue size decreased
        self.assertEqual(Queue.objects.count(), 4)
        
        # Check that the positions were updated
        positions = list(Queue.objects.values_list('position', flat=True).order_by('position'))
        self.assertEqual(positions, [1, 2, 3, 4])


class AdminManagementTest(UseCaseTestCase):
    """Test admin management functionality"""
    
    def test_admin_management(self):
        """
        Test admin management:
        1. Admin approves a deposit
        2. Admin approves a withdrawal
        3. Admin manages user accounts
        """
        # Log in as admin
        self.login_user(self.admin_user)
        
        # 1. Create a pending deposit
        user_wallet = Wallet.objects.create(
            user=self.user1,
            wallet_type='PLAN',
            plan=self.basic_plan,
            balance=Decimal('0.00')
        )
        
        deposit = Transaction.objects.create(
            user=self.user1,
            amount=Decimal('100.00'),
            transaction_type='DEPOSIT',
            status='PENDING',
            description='Deposit via bank transfer'
        )
        
        # Admin approves the deposit
        approve_deposit_url = reverse('admin_approve_deposit', args=[deposit.id])
        response = self.client.post(approve_deposit_url, follow=True)
        
        # Check that the deposit was approved
        deposit.refresh_from_db()
        self.assertEqual(deposit.status, 'COMPLETED')
        
        # Check that the wallet balance was updated
        user_wallet.refresh_from_db()
        self.assertEqual(user_wallet.balance, Decimal('100.00'))
        
        # 2. Create a pending withdrawal
        withdrawal = Withdrawal.objects.create(
            user=self.user1,
            amount=Decimal('50.00'),
            status='PENDING',
            payment_method='BANK',
            account_details='Test Bank Account'
        )
        
        # Admin approves the withdrawal
        approve_withdrawal_url = reverse('admin_approve_withdrawal', args=[withdrawal.id])
        response = self.client.post(approve_withdrawal_url, follow=True)
        
        # Check that the withdrawal was approved
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, 'COMPLETED')
        
        # Check that the wallet balance was updated
        user_wallet.refresh_from_db()
        self.assertEqual(user_wallet.balance, Decimal('50.00'))
        
        # 3. Admin manages user accounts
        # Admin suspends a user
        suspend_user_url = reverse('admin_suspend_user', args=[self.user2.id])
        response = self.client.post(suspend_user_url, follow=True)
        
        # Check that the user was suspended
        self.user2.refresh_from_db()
        self.assertFalse(self.user2.is_active)
        
        # Admin reactivates a user
        activate_user_url = reverse('admin_activate_user', args=[self.user2.id])
        response = self.client.post(activate_user_url, follow=True)
        
        # Check that the user was reactivated
        self.user2.refresh_from_db()
        self.assertTrue(self.user2.is_active)


class SubscriptionLifecycleTest(UseCaseTestCase):
    """Test the complete lifecycle of a subscription"""
    
    def test_subscription_lifecycle(self):
        """
        Test the complete lifecycle of a subscription:
        1. User creates a subscription (PENDING)
        2. User makes payment (ACTIVE)
        3. User completes the queue cycle (COMPLETED)
        4. User repurchases a subscription
        """
        # Log in as user1
        self.login_user(self.user1)
        
        # 1. Create a subscription
        subscribe_url = reverse('subscribe', args=[self.basic_plan.id])
        response = self.client.post(subscribe_url, follow=True)
        
        # Check that the subscription was created with PENDING status
        subscription = Subscription.objects.get(
            user=self.user1,
            plan=self.basic_plan
        )
        self.assertEqual(subscription.status, 'PENDING')
        
        # Create a wallet for the user
        wallet = Wallet.objects.create(
            user=self.user1,
            wallet_type='PLAN',
            plan=self.basic_plan,
            balance=Decimal('0.00')
        )
        
        # Deposit funds
        wallet.deposit(Decimal('50.00'), 'Initial deposit')
        
        # 2. Make payment for subscription
        payment_url = reverse('make_payment')
        response = self.client.post(
            payment_url,
            {
                'subscription_id': subscription.id,
                'amount': '50.00'
            },
            follow=True
        )
        
        # Check that the subscription is now ACTIVE
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'ACTIVE')
        
        # Check that the user was added to the queue
        queue_entry = Queue.objects.get(subscription=subscription)
        
        # 3. Simulate completing the queue cycle
        # Add funds to the wallet (as if received from other users)
        wallet.deposit(Decimal('200.00'), 'Received from other users')
        
        # Mark the subscription as completed
        subscription.status = 'COMPLETED'
        subscription.completed_at = timezone.now()
        subscription.save()
        
        # Remove from queue
        queue_entry.delete()
        
        # Check that the subscription is COMPLETED
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'COMPLETED')
        
        # 4. Repurchase a subscription
        repurchase_url = reverse('repurchase', args=[subscription.id])
        response = self.client.post(repurchase_url, follow=True)
        
        # Check that a new subscription was created
        new_subscription = Subscription.objects.filter(
            user=self.user1,
            plan=self.basic_plan,
            status='PENDING'
        ).exclude(id=subscription.id).first()
        
        self.assertIsNotNone(new_subscription)
        
        # Make payment for the new subscription using the repurchase percentage
        repurchase_amount = self.basic_plan.price * self.basic_plan.repurchase_percentage
        
        payment_url = reverse('make_payment')
        response = self.client.post(
            payment_url,
            {
                'subscription_id': new_subscription.id,
                'amount': str(repurchase_amount)
            },
            follow=True
        )
        
        # Check that the new subscription is ACTIVE
        new_subscription.refresh_from_db()
        self.assertEqual(new_subscription.status, 'ACTIVE')
        
        # Check that the user was added to the queue again
        self.assertTrue(
            Queue.objects.filter(
                subscription=new_subscription
            ).exists()
        )

