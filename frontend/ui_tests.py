from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from subscriptions.models import Plan, Subscription, Wallet
from decimal import Decimal
import json

User = get_user_model()

class UITestCase(TestCase):
    """Base test case for UI tests with common setup"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123",
            is_staff=True,
            is_superuser=True
        )
        
        # Create test plan
        self.plan = Plan.objects.create(
            name="Test Plan",
            price=Decimal("100.00"),
            queue_size=13,
            repurchase_percentage=Decimal("0.10"),
            maintenance_percentage=Decimal("0.05")
        )
        
        # Create client
        self.client = Client()
        
        # URLs
        self.home_url = reverse('home')
        self.dashboard_url = reverse('dashboard')
        self.login_url = reverse('account_login')
        self.signup_url = reverse('account_signup')
        self.plans_url = reverse('plans')
        
    def login_user(self, username="testuser", password="testpassword123"):
        """Helper method to log in a user"""
        self.client.login(username=username, password=password)


class HomePageTests(UITestCase):
    """Test the home page"""
    
    def test_home_page_loads(self):
        """Test that the home page loads successfully"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_home_page_contains_expected_content(self):
        """Test that the home page contains expected content"""
        response = self.client.get(self.home_url)
        self.assertContains(response, 'Agape')  # Assuming the site name is in the home page
        
    def test_home_page_has_register_link(self):
        """Test that the home page has a register link"""
        response = self.client.get(self.home_url)
        self.assertContains(response, 'signup')  # Assuming there's a signup link
        
    def test_home_page_has_login_link(self):
        """Test that the home page has a login link"""
        response = self.client.get(self.home_url)
        self.assertContains(response, 'login')  # Assuming there's a login link


class AuthenticationTests(UITestCase):
    """Test authentication flows"""
    
    def test_login_page_loads(self):
        """Test that the login page loads successfully"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        
    def test_signup_page_loads(self):
        """Test that the signup page loads successfully"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        
    def test_user_can_login(self):
        """Test that a user can log in"""
        response = self.client.post(
            self.login_url,
            {'login': 'testuser', 'password': 'testpassword123'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        
    def test_user_can_signup(self):
        """Test that a user can sign up"""
        response = self.client.post(
            self.signup_url,
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'newuserpassword123',
                'password2': 'newuserpassword123'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
    def test_login_required_for_dashboard(self):
        """Test that login is required to access the dashboard"""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(
            response, 
            f'/accounts/login/?next={self.dashboard_url}',
            fetch_redirect_response=False
        )


class DashboardTests(UITestCase):
    """Test the dashboard page"""
    
    def test_dashboard_loads_when_logged_in(self):
        """Test that the dashboard loads when logged in"""
        self.login_user()
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        
    def test_dashboard_shows_user_info(self):
        """Test that the dashboard shows user info"""
        self.login_user()
        response = self.client.get(self.dashboard_url)
        self.assertContains(response, self.user.username)
        
    def test_dashboard_shows_subscription_info_when_subscribed(self):
        """Test that the dashboard shows subscription info when subscribed"""
        self.login_user()
        
        # Create a subscription for the user
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE'
        )
        
        response = self.client.get(self.dashboard_url)
        self.assertContains(response, self.plan.name)


class PlansPageTests(UITestCase):
    """Test the plans page"""
    
    def test_plans_page_loads(self):
        """Test that the plans page loads successfully"""
        response = self.client.get(self.plans_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/plans.html')
        
    def test_plans_page_shows_available_plans(self):
        """Test that the plans page shows available plans"""
        response = self.client.get(self.plans_url)
        self.assertContains(response, self.plan.name)
        self.assertContains(response, str(self.plan.price))
        
    def test_authenticated_user_can_subscribe_to_plan(self):
        """Test that an authenticated user can subscribe to a plan"""
        self.login_user()
        
        # Assuming there's a subscribe URL that takes a plan ID
        subscribe_url = reverse('subscribe', args=[self.plan.id])
        
        response = self.client.post(subscribe_url, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that a subscription was created
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                plan=self.plan
            ).exists()
        )


class ReferralTests(UITestCase):
    """Test referral functionality"""
    
    def test_register_with_referral_code(self):
        """Test registering with a referral code"""
        # Set a referral code for the test user
        self.user.referral_code = 'TEST123'
        self.user.save()
        
        # Visit the register page with the referral code
        register_url = reverse('register') + '?ref=TEST123'
        response = self.client.get(register_url, follow=True)
        
        # Check that the referral code was stored in the session
        self.assertEqual(self.client.session.get('referral_code'), 'TEST123')
        
        # Register a new user
        response = self.client.post(
            self.signup_url,
            {
                'username': 'referreduser',
                'email': 'referred@example.com',
                'password1': 'referredpassword123',
                'password2': 'referredpassword123'
            },
            follow=True
        )
        
        # Check that the referral was created
        self.assertTrue(
            User.objects.filter(username='referreduser').exists()
        )
        
        # Check that a referral record was created
        referred_user = User.objects.get(username='referreduser')
        self.assertTrue(
            Referral.objects.filter(
                referrer=self.user,
                referred=referred_user
            ).exists()
        )


class WalletTests(UITestCase):
    """Test wallet functionality"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create a wallet for the test user
        self.wallet = Wallet.objects.create(
            user=self.user,
            wallet_type='PLAN',
            plan=self.plan,
            balance=Decimal('0.00')
        )
        
        # URL for wallet page
        self.wallet_url = reverse('wallet')
        
    def test_wallet_page_loads_when_logged_in(self):
        """Test that the wallet page loads when logged in"""
        self.login_user()
        response = self.client.get(self.wallet_url)
        self.assertEqual(response.status_code, 200)
        
    def test_wallet_page_shows_balance(self):
        """Test that the wallet page shows the balance"""
        self.login_user()
        
        # Add some funds to the wallet
        self.wallet.deposit(Decimal('50.00'), 'Test deposit')
        
        response = self.client.get(self.wallet_url)
        self.assertContains(response, '50.00')
        
    def test_user_can_request_withdrawal(self):
        """Test that a user can request a withdrawal"""
        self.login_user()
        
        # Add some funds to the wallet
        self.wallet.deposit(Decimal('100.00'), 'Test deposit')
        
        # Request a withdrawal
        withdrawal_url = reverse('request_withdrawal')
        response = self.client.post(
            withdrawal_url,
            {
                'amount': '50.00',
                'wallet': self.wallet.id,
                'payment_method': 'BANK',
                'account_details': 'Test Bank Account'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check that a withdrawal request was created
        from transactions.models import Withdrawal
        self.assertTrue(
            Withdrawal.objects.filter(
                user=self.user,
                amount=Decimal('50.00'),
                status='PENDING'
            ).exists()
        )


class AdminTests(UITestCase):
    """Test admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # URLs for admin pages
        self.admin_dashboard_url = reverse('admin_dashboard')
        self.admin_users_url = reverse('admin_users')
        self.admin_deposits_url = reverse('admin_deposits')
        self.admin_withdrawals_url = reverse('admin_withdrawals')
        
    def test_admin_dashboard_requires_staff_user(self):
        """Test that the admin dashboard requires a staff user"""
        # Try to access as a regular user
        self.login_user()
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Access as an admin user
        self.login_user('adminuser', 'adminpassword123')
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        
    def test_admin_can_view_users(self):
        """Test that an admin can view users"""
        self.login_user('adminuser', 'adminpassword123')
        response = self.client.get(self.admin_users_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        
    def test_admin_can_view_deposits(self):
        """Test that an admin can view deposits"""
        self.login_user('adminuser', 'adminpassword123')
        
        # Create a deposit
        wallet = Wallet.objects.create(
            user=self.user,
            wallet_type='PLAN',
            plan=self.plan,
            balance=Decimal('0.00')
        )
        wallet.deposit(Decimal('100.00'), 'Test deposit')
        
        response = self.client.get(self.admin_deposits_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '100.00')
        
    def test_admin_can_view_withdrawals(self):
        """Test that an admin can view withdrawals"""
        self.login_user('adminuser', 'adminpassword123')
        
        # Create a wallet with funds
        wallet = Wallet.objects.create(
            user=self.user,
            wallet_type='PLAN',
            plan=self.plan,
            balance=Decimal('100.00')
        )
        
        # Create a withdrawal request
        from transactions.models import Withdrawal
        withdrawal = Withdrawal.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            status='PENDING',
            payment_method='BANK',
            account_details='Test Bank Account'
        )
        
        response = self.client.get(self.admin_withdrawals_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '50.00')

