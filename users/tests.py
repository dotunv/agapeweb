from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from knox.models import AuthToken
from decimal import Decimal

User = get_user_model()

class UserModelTests(TestCase):
    """
    Test suite for the User model
    """

    def test_create_user(self):
        """
        Test creating a user with email and password
        """
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("testpassword123"))
        self.assertIsNotNone(user.referral_code)
        self.assertEqual(len(user.referral_code), 10)

    def test_create_superuser(self):
        """
        Test creating a superuser
        """
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword123"
        )

        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertEqual(admin_user.username, "admin")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.check_password("adminpassword123"))

    def test_referral_code_generation(self):
        """
        Test that a referral code is automatically generated
        """
        user = User.objects.create_user(
            username="referraluser",
            email="referral@example.com",
            password="password123"
        )

        self.assertIsNotNone(user.referral_code)
        self.assertEqual(len(user.referral_code), 10)

        # Test that the referral code is unique
        user2 = User.objects.create_user(
            username="referraluser2",
            email="referral2@example.com",
            password="password123"
        )

        self.assertNotEqual(user.referral_code, user2.referral_code)

    def test_wallet_fields_default_to_zero(self):
        """
        Test that all wallet fields default to zero
        """
        user = User.objects.create_user(
            username="walletuser",
            email="wallet@example.com",
            password="password123"
        )

        self.assertEqual(user.pre_starter_wallet, Decimal('0'))
        self.assertEqual(user.starter_wallet, Decimal('0'))
        self.assertEqual(user.basic1_wallet, Decimal('0'))
        self.assertEqual(user.basic2_wallet, Decimal('0'))
        self.assertEqual(user.standard_wallet, Decimal('0'))
        self.assertEqual(user.ultimate1_wallet, Decimal('0'))
        self.assertEqual(user.ultimate2_wallet, Decimal('0'))
        self.assertEqual(user.referral_bonus_wallet, Decimal('0'))
        self.assertEqual(user.funding_wallet, Decimal('0'))

class UserAPITests(APITestCase):
    """
    Test suite for the User API endpoints
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
        self.register_url = reverse('register')
        self.login_url = reverse('knox_login')
        self.me_url = reverse('user-me')

    def test_user_registration(self):
        """
        Test user registration endpoint
        """
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newuserpassword123',
            'password2': 'newuserpassword123'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)

        # Check that the user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_registration_password_mismatch(self):
        """
        Test user registration with mismatched passwords
        """
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newuserpassword123',
            'password2': 'differentpassword'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login(self):
        """
        Test user login endpoint
        """
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_user_login_invalid_credentials(self):
        """
        Test user login with invalid credentials
        """
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_profile(self):
        """
        Test retrieving user profile
        """
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_get_user_profile_unauthenticated(self):
        """
        Test retrieving user profile without authentication
        """
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
