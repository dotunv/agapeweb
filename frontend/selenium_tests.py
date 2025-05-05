from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from subscriptions.models import Plan, Subscription, Wallet
from decimal import Decimal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os

User = get_user_model()

class SeleniumTestCase(LiveServerTestCase):
    """Base test case for Selenium tests with common setup"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Set up the Selenium webdriver
        # Note: This requires Chrome and chromedriver to be installed
        # For CI environments, you might want to use headless mode
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
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
    
    def login(self, username="testuser", password="testpassword123"):
        """Helper method to log in a user using Selenium"""
        self.selenium.get(f'{self.live_server_url}{reverse("account_login")}')
        
        # Fill in the login form
        username_input = self.selenium.find_element(By.NAME, "login")
        password_input = self.selenium.find_element(By.NAME, "password")
        
        username_input.send_keys(username)
        password_input.send_keys(password)
        
        # Submit the form
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for the dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('dashboard')
        )


class AuthenticationSeleniumTests(SeleniumTestCase):
    """Test authentication flows using Selenium"""
    
    def test_login(self):
        """Test that a user can log in using the UI"""
        self.selenium.get(f'{self.live_server_url}{reverse("account_login")}')
        
        # Fill in the login form
        username_input = self.selenium.find_element(By.NAME, "login")
        password_input = self.selenium.find_element(By.NAME, "password")
        
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword123")
        
        # Submit the form
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for the dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('dashboard')
        )
        
        # Check that we're logged in
        self.assertIn('dashboard', self.selenium.current_url)
    
    def test_signup(self):
        """Test that a user can sign up using the UI"""
        self.selenium.get(f'{self.live_server_url}{reverse("account_signup")}')
        
        # Fill in the signup form
        username_input = self.selenium.find_element(By.NAME, "username")
        email_input = self.selenium.find_element(By.NAME, "email")
        password1_input = self.selenium.find_element(By.NAME, "password1")
        password2_input = self.selenium.find_element(By.NAME, "password2")
        
        username_input.send_keys("newseleniumuser")
        email_input.send_keys("selenium@example.com")
        password1_input.send_keys("seleniumpassword123")
        password2_input.send_keys("seleniumpassword123")
        
        # Submit the form
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for the dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('dashboard')
        )
        
        # Check that the user was created
        self.assertTrue(
            User.objects.filter(username="newseleniumuser").exists()
        )


class DashboardSeleniumTests(SeleniumTestCase):
    """Test dashboard functionality using Selenium"""
    
    def test_dashboard_displays_user_info(self):
        """Test that the dashboard displays user information"""
        # Log in
        self.login()
        
        # Wait for the dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container"))
        )
        
        # Check that the username is displayed
        self.assertIn(
            "testuser",
            self.selenium.find_element(By.TAG_NAME, "body").text
        )
    
    def test_dashboard_displays_subscription_info(self):
        """Test that the dashboard displays subscription information"""
        # Create a subscription for the user
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE'
        )
        
        # Log in
        self.login()
        
        # Wait for the dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container"))
        )
        
        # Check that the plan name is displayed
        self.assertIn(
            "Test Plan",
            self.selenium.find_element(By.TAG_NAME, "body").text
        )


class PlansSeleniumTests(SeleniumTestCase):
    """Test plans page functionality using Selenium"""
    
    def test_plans_page_displays_plans(self):
        """Test that the plans page displays available plans"""
        # Log in
        self.login()
        
        # Navigate to the plans page
        self.selenium.get(f'{self.live_server_url}{reverse("plans")}')
        
        # Wait for the plans to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "plan-card"))
        )
        
        # Check that the plan name is displayed
        self.assertIn(
            "Test Plan",
            self.selenium.find_element(By.TAG_NAME, "body").text
        )
        
        # Check that the plan price is displayed
        self.assertIn(
            "$100.00",
            self.selenium.find_element(By.TAG_NAME, "body").text
        )
    
    def test_user_can_subscribe_to_plan(self):
        """Test that a user can subscribe to a plan"""
        # Log in
        self.login()
        
        # Navigate to the plans page
        self.selenium.get(f'{self.live_server_url}{reverse("plans")}')
        
        # Wait for the plans to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "plan-card"))
        )
        
        # Click the subscribe button
        self.selenium.find_element(By.CLASS_NAME, "subscribe-btn").click()
        
        # Wait for the subscription confirmation page
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('subscribe-confirmation')
        )
        
        # Check that a subscription was created
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                plan=self.plan
            ).exists()
        )


class WalletSeleniumTests(SeleniumTestCase):
    """Test wallet functionality using Selenium"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create a wallet for the test user
        self.wallet = Wallet.objects.create(
            user=self.user,
            wallet_type='PLAN',
            plan=self.plan,
            balance=Decimal('100.00')
        )
    
    def test_wallet_page_displays_balance(self):
        """Test that the wallet page displays the balance"""
        # Log in
        self.login()
        
        # Navigate to the wallet page
        self.selenium.get(f'{self.live_server_url}{reverse("wallet")}')
        
        # Wait for the wallet to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wallet-container"))
        )
        
        # Check that the balance is displayed
        self.assertIn(
            "$100.00",
            self.selenium.find_element(By.TAG_NAME, "body").text
        )
    
    def test_user_can_request_withdrawal(self):
        """Test that a user can request a withdrawal"""
        # Log in
        self.login()
        
        # Navigate to the wallet page
        self.selenium.get(f'{self.live_server_url}{reverse("wallet")}')
        
        # Wait for the wallet to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wallet-container"))
        )
        
        # Click the withdraw button
        self.selenium.find_element(By.ID, "withdraw-btn").click()
        
        # Wait for the withdrawal form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "withdrawal-form"))
        )
        
        # Fill in the withdrawal form
        amount_input = self.selenium.find_element(By.NAME, "amount")
        payment_method_select = self.selenium.find_element(By.NAME, "payment_method")
        account_details_input = self.selenium.find_element(By.NAME, "account_details")
        
        amount_input.send_keys("50.00")
        payment_method_select.send_keys("BANK")
        account_details_input.send_keys("Test Bank Account")
        
        # Submit the form
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for the confirmation message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        # Check that a withdrawal request was created
        from transactions.models import Withdrawal
        self.assertTrue(
            Withdrawal.objects.filter(
                user=self.user,
                amount=Decimal('50.00'),
                status='PENDING'
            ).exists()
        )


class AdminSeleniumTests(SeleniumTestCase):
    """Test admin functionality using Selenium"""
    
    def test_admin_can_manage_users(self):
        """Test that an admin can manage users"""
        # Log in as admin
        self.login("adminuser", "adminpassword123")
        
        # Navigate to the admin users page
        self.selenium.get(f'{self.live_server_url}{reverse("admin_users")}')
        
        # Wait for the users table to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "users-table"))
        )
        
        # Check that the test user is listed
        self.assertIn(
            "testuser",
            self.selenium.find_element(By.TAG_NAME, "body").text
        )
        
        # Click the suspend button for the test user
        suspend_button = self.selenium.find_element(By.XPATH, f"//tr[contains(., 'testuser')]//button[contains(@class, 'suspend-btn')]")
        suspend_button.click()
        
        # Wait for the confirmation dialog
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "confirmation-dialog"))
        )
        
        # Confirm the suspension
        confirm_button = self.selenium.find_element(By.XPATH, "//button[contains(@class, 'confirm-btn')]")
        confirm_button.click()
        
        # Wait for the success message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        # Check that the user was suspended
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
    
    def test_admin_can_approve_withdrawals(self):
        """Test that an admin can approve withdrawals"""
        # Create a withdrawal request
        from transactions.models import Withdrawal
        withdrawal = Withdrawal.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            status='PENDING',
            payment_method='BANK',
            account_details='Test Bank Account'
        )
        
        # Log in as admin
        self.login("adminuser", "adminpassword123")
        
        # Navigate to the admin withdrawals page
        self.selenium.get(f'{self.live_server_url}{reverse("admin_withdrawals")}')
        
        # Wait for the withdrawals table to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "withdrawals-table"))
        )
        
        # Check that the withdrawal is listed
        self.assertIn(
            "$50.00",
            self.selenium.find_element(By.TAG_NAME, "body").text
        )
        
        # Click the approve button for the withdrawal
        approve_button = self.selenium.find_element(By.XPATH, f"//tr[contains(., '$50.00')]//button[contains(@class, 'approve-btn')]")
        approve_button.click()
        
        # Wait for the confirmation dialog
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "confirmation-dialog"))
        )
        
        # Confirm the approval
        confirm_button = self.selenium.find_element(By.XPATH, "//button[contains(@class, 'confirm-btn')]")
        confirm_button.click()
        
        # Wait for the success message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        # Check that the withdrawal was approved
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, 'COMPLETED')

