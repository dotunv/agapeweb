from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Plan, Subscription, Queue, Wallet, Referral, Contribution

User = get_user_model()

class PlanModelTests(TestCase):
    """
    Test suite for the Plan model
    """

    def setUp(self):
        """
        Set up test data
        """
        self.plan = Plan.objects.create(
            name="Test Plan",
            price=Decimal("100.00"),
            queue_size=13,
            repurchase_percentage=Decimal("0.10"),
            maintenance_percentage=Decimal("0.05")
        )

    def test_plan_creation(self):
        """
        Test creating a plan
        """
        self.assertEqual(self.plan.name, "Test Plan")
        self.assertEqual(self.plan.price, Decimal("100.00"))
        self.assertEqual(self.plan.queue_size, 13)
        self.assertEqual(self.plan.repurchase_percentage, Decimal("0.10"))
        self.assertEqual(self.plan.maintenance_percentage, Decimal("0.05"))
        self.assertEqual(str(self.plan), "Test Plan - $100.00")

class SubscriptionModelTests(TestCase):
    """
    Test suite for the Subscription model
    """

    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        self.plan = Plan.objects.create(
            name="Test Plan",
            price=Decimal("100.00"),
            queue_size=13,
            repurchase_percentage=Decimal("0.10"),
            maintenance_percentage=Decimal("0.05")
        )

        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="PENDING"
        )

    def test_subscription_creation(self):
        """
        Test creating a subscription
        """
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.plan, self.plan)
        self.assertEqual(self.subscription.status, "PENDING")
        self.assertIsNone(self.subscription.approved_at)
        self.assertIsNone(self.subscription.completed_at)
        self.assertEqual(str(self.subscription), f"{self.user.username} - Test Plan - PENDING")

    def test_subscription_process_payment(self):
        """
        Test processing a payment for a subscription
        """
        # Create a second subscription to make a payment
        user2 = User.objects.create_user(
            username="payer",
            email="payer@example.com",
            password="password123"
        )

        payer_subscription = Subscription.objects.create(
            user=user2,
            plan=self.plan,
            status="ACTIVE"
        )

        # Process payment
        self.subscription.status = "ACTIVE"
        self.subscription.save()

        result = self.subscription.process_payment(payer_subscription, Decimal("100.00"))

        # Check that the payment was processed
        self.assertTrue(result)

        # Check that a contribution was created
        self.assertEqual(Contribution.objects.count(), 1)
        contribution = Contribution.objects.first()
        self.assertEqual(contribution.from_subscription, payer_subscription)
        self.assertEqual(contribution.to_subscription, self.subscription)
        self.assertEqual(contribution.amount, Decimal("100.00"))

class QueueModelTests(TestCase):
    """
    Test suite for the Queue model
    """

    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        self.plan = Plan.objects.create(
            name="Test Plan",
            price=Decimal("100.00"),
            queue_size=3,  # Small queue for testing
            repurchase_percentage=Decimal("0.10"),
            maintenance_percentage=Decimal("0.05")
        )

        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="ACTIVE"
        )

        # Create a queue for the plan
        self.queue = Queue.objects.create(
            plan=self.plan,
            position=1,
            subscription=self.subscription
        )

    def test_queue_creation(self):
        """
        Test creating a queue entry
        """
        self.assertEqual(self.queue.plan, self.plan)
        self.assertEqual(self.queue.position, 1)
        self.assertEqual(self.queue.subscription, self.subscription)
        self.assertEqual(str(self.queue), f"Position 1 - {self.user.username} - Test Plan")

    def test_add_to_queue(self):
        """
        Test adding a subscription to the queue
        """
        # Create a new user and subscription
        user2 = User.objects.create_user(
            username="queueuser",
            email="queue@example.com",
            password="password123"
        )

        subscription2 = Subscription.objects.create(
            user=user2,
            plan=self.plan,
            status="ACTIVE"
        )

        # Add to queue
        Queue.add_to_queue(subscription2)

        # Check that the subscription was added to the queue
        self.assertEqual(Queue.objects.count(), 2)
        queue_entry = Queue.objects.get(subscription=subscription2)
        self.assertEqual(queue_entry.position, 2)  # Should be position 2

    def test_shift_queue(self):
        """
        Test shifting the queue
        """
        # Create additional users and subscriptions
        for i in range(2):
            user = User.objects.create_user(
                username=f"queueuser{i}",
                email=f"queue{i}@example.com",
                password="password123"
            )

            subscription = Subscription.objects.create(
                user=user,
                plan=self.plan,
                status="ACTIVE"
            )

            Queue.add_to_queue(subscription)

        # Now we have 3 subscriptions in the queue
        self.assertEqual(Queue.objects.count(), 3)

        # Shift the queue
        self.queue.shift_queue()

        # Check that the first subscription was removed and others shifted
        self.assertEqual(Queue.objects.count(), 2)

        # Check positions were updated
        positions = list(Queue.objects.values_list('position', flat=True).order_by('position'))
        self.assertEqual(positions, [1, 2])

class WalletModelTests(TestCase):
    """
    Test suite for the Wallet model
    """

    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        self.plan = Plan.objects.create(
            name="Test Plan",
            price=Decimal("100.00"),
            queue_size=13,
            repurchase_percentage=Decimal("0.10"),
            maintenance_percentage=Decimal("0.05")
        )

        self.wallet = Wallet.objects.create(
            user=self.user,
            wallet_type="PLAN",
            plan=self.plan,
            balance=Decimal("0.00")
        )

    def test_wallet_creation(self):
        """
        Test creating a wallet
        """
        self.assertEqual(self.wallet.user, self.user)
        self.assertEqual(self.wallet.wallet_type, "PLAN")
        self.assertEqual(self.wallet.plan, self.plan)
        self.assertEqual(self.wallet.balance, Decimal("0.00"))
        self.assertEqual(str(self.wallet), f"{self.user.username} - PLAN - Test Plan - $0.00")

    def test_wallet_deposit(self):
        """
        Test depositing funds into a wallet
        """
        self.wallet.deposit(Decimal("50.00"), "Test deposit")

        self.assertEqual(self.wallet.balance, Decimal("50.00"))

        # Check that a transaction was created
        from transactions.models import Transaction
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal("50.00"))
        self.assertEqual(transaction.transaction_type, "DEPOSIT")
        self.assertEqual(transaction.status, "COMPLETED")

    def test_wallet_withdraw(self):
        """
        Test withdrawing funds from a wallet
        """
        # First deposit some funds
        self.wallet.deposit(Decimal("100.00"), "Initial deposit")

        # Then withdraw
        self.wallet.withdraw(Decimal("30.00"), "Test withdrawal")

        self.assertEqual(self.wallet.balance, Decimal("70.00"))

        # Check that a transaction was created
        from transactions.models import Transaction
        self.assertEqual(Transaction.objects.count(), 2)  # Deposit + withdrawal
        transaction = Transaction.objects.filter(transaction_type="WITHDRAWAL").first()
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal("30.00"))
        self.assertEqual(transaction.status, "COMPLETED")

    def test_wallet_withdraw_insufficient_funds(self):
        """
        Test withdrawing more than the wallet balance
        """
        with self.assertRaises(ValueError):
            self.wallet.withdraw(Decimal("50.00"), "Test withdrawal")

class SubscriptionAPITests(APITestCase):
    """
    Test suite for the Subscription API endpoints
    """

    def setUp(self):
        """
        Set up test data
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        self.plan = Plan.objects.create(
            name="Test Plan",
            price=Decimal("100.00"),
            queue_size=13,
            repurchase_percentage=Decimal("0.10"),
            maintenance_percentage=Decimal("0.05")
        )

        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="ACTIVE"
        )

        self.plans_url = reverse('plan-list')
        self.subscriptions_url = reverse('subscription-list')
        self.my_subscription_url = reverse('subscription-my-subscription')
        self.queue_position_url = reverse('subscription-queue-position')

    def test_list_plans(self):
        """
        Test listing all plans
        """
        response = self.client.get(self.plans_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Test Plan")

    def test_create_subscription(self):
        """
        Test creating a subscription
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'plan': self.plan.id
        }

        response = self.client.post(self.subscriptions_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plan'], self.plan.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['status'], "PENDING")

    def test_get_my_subscription(self):
        """
        Test retrieving the user's subscription
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.my_subscription_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.subscription.id)
        self.assertEqual(response.data[0]['plan'], self.plan.id)

    def test_get_queue_position(self):
        """
        Test retrieving the user's queue position
        """
        self.client.force_authenticate(user=self.user)

        # Add the subscription to the queue
        Queue.objects.create(
            plan=self.plan,
            position=1,
            subscription=self.subscription
        )

        response = self.client.get(self.queue_position_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['position'], 1)
        self.assertEqual(response.data['plan_name'], "Test Plan")
