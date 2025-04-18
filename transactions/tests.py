from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Transaction, Withdrawal
from subscriptions.models import Plan, Subscription, Wallet

User = get_user_model()

class TransactionModelTests(TestCase):
    """
    Test suite for the Transaction model
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

        self.transaction = Transaction.objects.create(
            user=self.user,
            transaction_type="DEPOSIT",
            amount=Decimal("100.00"),
            status="PENDING",
            transaction_id="test-transaction-id",
            description="Test transaction"
        )

    def test_transaction_creation(self):
        """
        Test creating a transaction
        """
        self.assertEqual(self.transaction.user, self.user)
        self.assertEqual(self.transaction.transaction_type, "DEPOSIT")
        self.assertEqual(self.transaction.amount, Decimal("100.00"))
        self.assertEqual(self.transaction.status, "PENDING")
        self.assertEqual(self.transaction.transaction_id, "test-transaction-id")
        self.assertEqual(self.transaction.description, "Test transaction")
        self.assertIsNone(self.transaction.completed_at)
        self.assertEqual(str(self.transaction), f"{self.user.username} - DEPOSIT - 100.00")

class WithdrawalModelTests(TestCase):
    """
    Test suite for the Withdrawal model
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

        self.transaction = Transaction.objects.create(
            user=self.user,
            transaction_type="WITHDRAWAL",
            amount=Decimal("100.00"),
            status="PENDING",
            transaction_id="test-withdrawal-id",
            description="Test withdrawal"
        )

        self.withdrawal = Withdrawal.objects.create(
            user=self.user,
            amount=Decimal("100.00"),
            status="PENDING",
            withdrawal_type="WALLET",
            transaction=self.transaction,
            withdrawal_fee=Decimal("5.00")
        )

    def test_withdrawal_creation(self):
        """
        Test creating a withdrawal
        """
        self.assertEqual(self.withdrawal.user, self.user)
        self.assertEqual(self.withdrawal.amount, Decimal("100.00"))
        self.assertEqual(self.withdrawal.status, "PENDING")
        self.assertEqual(self.withdrawal.withdrawal_type, "WALLET")
        self.assertEqual(self.withdrawal.transaction, self.transaction)
        self.assertEqual(self.withdrawal.withdrawal_fee, Decimal("5.00"))
        self.assertIsNone(self.withdrawal.processed_at)
        self.assertEqual(str(self.withdrawal), f"{self.user.username} - $100.00 - Wallet Withdrawal")

    def test_withdrawal_approve(self):
        """
        Test approving a withdrawal
        """
        self.withdrawal.approve()

        self.assertEqual(self.withdrawal.status, "APPROVED")
        self.assertIsNotNone(self.withdrawal.processed_at)

        # Check that the transaction status was updated
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, "COMPLETED")
        self.assertIsNotNone(self.transaction.completed_at)

    def test_withdrawal_reject(self):
        """
        Test rejecting a withdrawal
        """
        # Create a wallet for the refund
        plan = Plan.objects.create(
            name="Test Plan",
            price=Decimal("100.00"),
            queue_size=13,
            repurchase_percentage=Decimal("0.10"),
            maintenance_percentage=Decimal("0.05")
        )

        wallet = Wallet.objects.create(
            user=self.user,
            wallet_type="PLAN",
            plan=plan,
            balance=Decimal("0.00")
        )

        self.withdrawal.wallet = wallet
        self.withdrawal.save()

        self.withdrawal.reject()

        self.assertEqual(self.withdrawal.status, "REJECTED")
        self.assertIsNotNone(self.withdrawal.processed_at)

        # Check that the transaction status was updated
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, "FAILED")
        self.assertIsNotNone(self.transaction.completed_at)

        # Check that the amount was refunded to the wallet
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("100.00"))

    def test_withdrawal_fee_calculation(self):
        """
        Test that the withdrawal fee is calculated correctly
        """
        # Create a new withdrawal without specifying the fee
        transaction = Transaction.objects.create(
            user=self.user,
            transaction_type="WITHDRAWAL",
            amount=Decimal("200.00"),
            status="PENDING",
            transaction_id="test-withdrawal-fee-id",
            description="Test withdrawal fee"
        )

        withdrawal = Withdrawal.objects.create(
            user=self.user,
            amount=Decimal("200.00"),
            status="PENDING",
            withdrawal_type="WALLET",
            transaction=transaction
        )

        # Check that the fee was calculated as 5% of the amount
        self.assertEqual(withdrawal.withdrawal_fee, Decimal("10.00"))

class TransactionAPITests(APITestCase):
    """
    Test suite for the Transaction API endpoints
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

        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword123"
        )

        self.transaction = Transaction.objects.create(
            user=self.user,
            transaction_type="DEPOSIT",
            amount=Decimal("100.00"),
            status="COMPLETED",
            transaction_id="test-transaction-id",
            description="Test transaction"
        )

        self.transactions_url = reverse('transaction-list')

    def test_list_transactions(self):
        """
        Test listing user transactions
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.transactions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['transaction_type'], "DEPOSIT")
        self.assertEqual(response.data['results'][0]['amount'], '100.00')

    def test_list_transactions_unauthenticated(self):
        """
        Test listing transactions without authentication
        """
        response = self.client.get(self.transactions_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class WithdrawalAPITests(APITestCase):
    """
    Test suite for the Withdrawal API endpoints
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

        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword123"
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
            balance=Decimal("200.00")
        )

        self.transaction = Transaction.objects.create(
            user=self.user,
            transaction_type="WITHDRAWAL",
            amount=Decimal("100.00"),
            status="PENDING",
            transaction_id="test-withdrawal-id",
            description="Test withdrawal"
        )

        self.withdrawal = Withdrawal.objects.create(
            user=self.user,
            amount=Decimal("100.00"),
            status="PENDING",
            withdrawal_type="WALLET",
            transaction=self.transaction,
            withdrawal_fee=Decimal("5.00"),
            wallet=self.wallet
        )

        self.withdrawals_url = reverse('withdrawal-list')
        self.approve_url = reverse('withdrawal-approve', args=[self.withdrawal.id])
        self.reject_url = reverse('withdrawal-reject', args=[self.withdrawal.id])

    def test_create_withdrawal(self):
        """
        Test creating a withdrawal
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'amount': '50.00',
            'withdrawal_type': 'WALLET',
            'wallet': self.wallet.id
        }

        response = self.client.post(self.withdrawals_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data['amount']), Decimal('50.00'))
        self.assertEqual(response.data['withdrawal_type'], 'WALLET')
        self.assertEqual(response.data['status'], 'PENDING')

        # Check that a transaction was created
        self.assertEqual(Transaction.objects.count(), 2)

        # Check that the wallet balance was reduced
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('150.00'))  # 200 - 50

    def test_approve_withdrawal(self):
        """
        Test approving a withdrawal
        """
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.approve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'APPROVED')

        # Check that the withdrawal was approved
        self.withdrawal.refresh_from_db()
        self.assertEqual(self.withdrawal.status, 'APPROVED')

        # Check that the transaction was completed
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'COMPLETED')

    def test_reject_withdrawal(self):
        """
        Test rejecting a withdrawal
        """
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.reject_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'REJECTED')

        # Check that the withdrawal was rejected
        self.withdrawal.refresh_from_db()
        self.assertEqual(self.withdrawal.status, 'REJECTED')

        # Check that the transaction was failed
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'FAILED')

        # Check that the amount was refunded to the wallet
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('300.00'))  # 200 + 100
