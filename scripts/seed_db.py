import os
import sys
import django
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
import string

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agape.settings')
django.setup()

from django.contrib.auth import get_user_model
from plans.models import Plan, Subscription
from users.models import Notification

User = get_user_model()

def generate_random_string(length=10):
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_test_users():
    """Create test users with various scenarios."""
    users = []
    
    # Create admin user
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        phone_number='+1234567890',
        two_factor_enabled=True
    )
    users.append(admin)
    
    # Create regular users with different wallet balances
    regular_users = [
        {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'password123',
            'pre_starter_wallet': Decimal('100.00'),
            'starter_wallet': Decimal('50.00'),
        },
        {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'password123',
            'basic1_wallet': Decimal('200.00'),
            'basic2_wallet': Decimal('150.00'),
        },
        {
            'username': 'user3',
            'email': 'user3@example.com',
            'password': 'password123',
            'standard_wallet': Decimal('300.00'),
            'ultimate1_wallet': Decimal('250.00'),
        },
        {
            'username': 'user4',
            'email': 'user4@example.com',
            'password': 'password123',
            'ultimate2_wallet': Decimal('400.00'),
            'referral_bonus_wallet': Decimal('100.00'),
        },
        {
            'username': 'user5',
            'email': 'user5@example.com',
            'password': 'password123',
            'funding_wallet': Decimal('500.00'),
        }
    ]
    
    for user_data in regular_users:
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            phone_number=f'+1{random.randint(1000000000, 9999999999)}'
        )
        
        # Set wallet balances
        for wallet, amount in user_data.items():
            if wallet.endswith('_wallet'):
                setattr(user, wallet, amount)
        
        user.save()
        users.append(user)
    
    # Create users with failed login attempts
    locked_user = User.objects.create_user(
        username='locked_user',
        email='locked@example.com',
        password='password123',
        failed_login_attempts=5,
        account_locked_until=timezone.now() + timedelta(minutes=30)
    )
    users.append(locked_user)
    
    # Create users with referral relationships
    referrer = User.objects.create_user(
        username='referrer',
        email='referrer@example.com',
        password='password123'
    )
    users.append(referrer)
    
    for i in range(3):
        referred = User.objects.create_user(
            username=f'referred{i+1}',
            email=f'referred{i+1}@example.com',
            password='password123',
            referred_by=referrer
        )
        users.append(referred)
    
    return users

def create_test_plans():
    """Create test subscription plans."""
    plans = []
    
    plan_data = [
        {
            'name': 'Pre-Starter',
            'description': 'Basic plan for beginners',
            'price': Decimal('9.99'),
            'duration_days': 30,
            'features': ['Feature 1', 'Feature 2']
        },
        {
            'name': 'Starter',
            'description': 'Entry-level plan',
            'price': Decimal('19.99'),
            'duration_days': 30,
            'features': ['Feature 1', 'Feature 2', 'Feature 3']
        },
        {
            'name': 'Basic',
            'description': 'Standard plan',
            'price': Decimal('29.99'),
            'duration_days': 30,
            'features': ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']
        },
        {
            'name': 'Standard',
            'description': 'Professional plan',
            'price': Decimal('49.99'),
            'duration_days': 30,
            'features': ['All Basic features', 'Premium support']
        },
        {
            'name': 'Ultimate',
            'description': 'Premium plan',
            'price': Decimal('99.99'),
            'duration_days': 30,
            'features': ['All features', 'Priority support', 'Custom solutions']
        }
    ]
    
    for data in plan_data:
        plan = Plan.objects.create(**data)
        plans.append(plan)
    
    return plans

def create_test_subscriptions(users, plans):
    """Create test subscriptions with various statuses."""
    subscriptions = []
    
    # Create active subscriptions
    for user in users[1:4]:  # Skip admin
        plan = random.choice(plans)
        start_date = timezone.now() - timedelta(days=random.randint(1, 15))
        end_date = start_date + timedelta(days=plan.duration_days)
        
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            status=Subscription.SubscriptionStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date
        )
        subscriptions.append(subscription)
    
    # Create cancelled subscriptions
    for user in users[4:6]:
        plan = random.choice(plans)
        start_date = timezone.now() - timedelta(days=random.randint(30, 60))
        end_date = start_date + timedelta(days=plan.duration_days)
        
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            status=Subscription.SubscriptionStatus.CANCELLED,
            start_date=start_date,
            end_date=end_date
        )
        subscriptions.append(subscription)
    
    # Create expired subscriptions
    for user in users[6:8]:
        plan = random.choice(plans)
        start_date = timezone.now() - timedelta(days=random.randint(60, 90))
        end_date = start_date + timedelta(days=plan.duration_days)
        
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            status=Subscription.SubscriptionStatus.EXPIRED,
            start_date=start_date,
            end_date=end_date
        )
        subscriptions.append(subscription)
    
    # Create pending subscriptions
    for user in users[8:10]:
        plan = random.choice(plans)
        start_date = timezone.now()
        end_date = start_date + timedelta(days=plan.duration_days)
        
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            status=Subscription.SubscriptionStatus.PENDING,
            start_date=start_date,
            end_date=end_date
        )
        subscriptions.append(subscription)
    
    return subscriptions

def create_test_notifications(users):
    """Create test notifications for users."""
    notifications = []
    notification_types = ['info', 'success', 'warning', 'error']
    
    for user in users:
        for _ in range(random.randint(1, 5)):
            notification = Notification.objects.create(
                user=user,
                title=f'Test Notification {generate_random_string(5)}',
                message=f'This is a test notification message. {generate_random_string(20)}',
                notification_type=random.choice(notification_types),
                read=random.choice([True, False])
            )
            notifications.append(notification)
    
    return notifications

def seed_database():
    """Main function to seed the database with test data."""
    print("Starting database seeding...")
    
    # Clear existing data
    print("Clearing existing data...")
    User.objects.all().delete()
    Plan.objects.all().delete()
    Subscription.objects.all().delete()
    Notification.objects.all().delete()
    
    # Create test data
    print("Creating test users...")
    users = create_test_users()
    
    print("Creating test plans...")
    plans = create_test_plans()
    
    print("Creating test subscriptions...")
    subscriptions = create_test_subscriptions(users, plans)
    
    print("Creating test notifications...")
    notifications = create_test_notifications(users)
    
    print("Database seeding completed successfully!")
    print(f"Created {len(users)} users")
    print(f"Created {len(plans)} plans")
    print(f"Created {len(subscriptions)} subscriptions")
    print(f"Created {len(notifications)} notifications")

if __name__ == '__main__':
    seed_database() 