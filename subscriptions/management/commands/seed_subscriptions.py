from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription, Plan
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seed the database with test subscriptions and users.'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Create test plans if they don't exist
        plans = [
            ('Basic 1', 100),
            ('Basic 2', 500),
            ('Standard', 1000),
            ('Ultimate 1', 2500),
            ('Starters Pack', 25),
        ]
        plan_objs = []
        for name, amount in plans:
            plan, _ = Plan.objects.get_or_create(
                name=name,
                defaults={
                    'contribution_amount': amount,
                    'total_received': 0,
                    'max_members': 100,
                    'deduction_repurchase': 0,
                    'deduction_maintenance': 0,
                    'withdrawable_amount': 0,
                    'plan_type': name.upper().replace(' ', '_'),
                }
            )
            plan_objs.append(plan)

        # Create a superuser for admin testing
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')

        # Create a variety of users
        users = []
        for i in range(10):
            username = f'testuser{i+1}'
            email = f'testuser{i+1}@example.com'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            # Set password if just created
            if created:
                user.set_password('testpassword')
                user.save()
            users.append(user)

        # Edge case: user with no subscriptions
        user_no_subs, _ = User.objects.get_or_create(username='nosubs', defaults={'email': 'nosubs@example.com'})
        if not user_no_subs.check_password('testpassword'):
            user_no_subs.set_password('testpassword')
            user_no_subs.save()
        users.append(user_no_subs)

        # Edge case: user with many subscriptions
        user_many_subs, _ = User.objects.get_or_create(username='manysubs', defaults={'email': 'manysubs@example.com'})
        if not user_many_subs.check_password('testpassword'):
            user_many_subs.set_password('testpassword')
            user_many_subs.save()
        users.append(user_many_subs)

        # Create subscriptions for regular users
        for i in range(30):
            user = random.choice(users[:-2])  # Exclude edge case users for random
            plan = random.choice(plan_objs)
            joined_at = timezone.now() - timezone.timedelta(days=random.randint(1, 365))
            Subscription.objects.create(
                user=user,
                plan=plan,
                joined_at=joined_at,
                total_received=plan.contribution_amount,
            )
        # Edge case: user with many subscriptions
        for i in range(15):
            plan = random.choice(plan_objs)
            joined_at = timezone.now() - timezone.timedelta(days=random.randint(1, 365))
            Subscription.objects.create(
                user=user_many_subs,
                plan=plan,
                joined_at=joined_at,
                total_received=plan.contribution_amount,
            )
        # No subscriptions for user_no_subs
        self.stdout.write(self.style.SUCCESS('Seeded: superuser, regular users, user with no subs, user with many subs, all plan types, and subscriptions for dev scenarios!'))
