from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib import messages
from users.models import User, Notification
from subscriptions.models import Subscription, Plan, Referral, Wallet
from transactions.models import Transaction, Withdrawal
from django.http import JsonResponse
from .models import Payment
from decimal import Decimal
import json
import uuid
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

def home(request):
    """Home page view."""
    return render(request, 'home.html')

def register(request):
    """Handle registration with referral code."""
    referral_code = request.GET.get('ref')
    if referral_code:
        try:
            referrer = User.objects.get(referral_code=referral_code)
            messages.info(request, f'Registering with referral from {referrer.username}')
            # Store referral code in session
            request.session['referral_code'] = referral_code
        except User.DoesNotExist:
            messages.warning(request, 'Invalid referral code.')
    
    return redirect('account_signup')

@login_required
def dashboard(request):
    """User dashboard view."""
    # Get user's active subscription if any
    user_plan = Subscription.objects.filter(user=request.user, status='active').first()
    
    # Prepare current plan data if exists
    current_plan = None
    if user_plan:
        current_plan = {
            'name': user_plan.plan.name,
            'status': user_plan.status,
            'current_cycle': 1,  # You may need to calculate this based on your business logic
            'total_cycles': 1,   # You may need to calculate this based on your business logic
            'progress_percentage': 0  # You may need to calculate this based on your business logic
        }
    
    # Get recent subscriptions with plan prices
    recent_subscriptions = []
    for sub in Subscription.objects.filter(user=request.user).order_by('-joined_at')[:5]:
        recent_subscriptions.append({
            'user': sub.user,
            'created_at': sub.joined_at,
            'amount': sub.plan.contribution_amount
        })
    
    context = {
        'user_balance': request.user.balance,
        'recent_subscriptions': recent_subscriptions,
        'available_plans': Plan.objects.all(),
        'user_plan': user_plan,
        'current_plan': current_plan,
        'unread_notifications_count': request.user.notifications.filter(read=False).count()
    }
    return render(request, 'dashboard/dashboard.html', context)

WALLET_ADDRESS = "0xF6823b403aC8d2A682CdF8b47299A85AaD8265ADC"

@login_required
def fund_account(request):
    if request.method == 'GET':
        context = {
            'wallet_address': WALLET_ADDRESS
        }
        return render(request, 'dashboard/fund_account.html', context)
    
    elif request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            transaction_id = request.POST.get('transaction_id', '').strip()
            token_id = request.POST.get('token_id', '').strip()

            if not all([amount, transaction_id, token_id]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please fill in all required fields.'
                }, status=400)

            if amount <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Amount must be greater than 0.'
                }, status=400)

            # Check if transaction_id is unique
            if Payment.objects.filter(transaction_id=transaction_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Transaction ID already exists.'
                }, status=400)

            # Create new payment record
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                transaction_id=transaction_id,
                token_id=token_id,
                status='pending'
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Payment submitted successfully. Our team will verify your transaction.',
                'payment_id': payment.id
            })

        except (ValueError, decimal.InvalidOperation):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid amount provided.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'An unexpected error occurred. Please try again.'
            }, status=500)

@login_required
def plans(request):
    """Available plans view."""
    # Get user's active subscription if any
    user_plan = Subscription.objects.filter(user=request.user, status='active').first()
    
    context = {
        'plans': Plan.objects.all(),
        'user_plan': user_plan
    }
    return render(request, 'dashboard/plans.html', context)

from django.core.paginator import Paginator

@login_required
def subscriptions(request):
    """User subscriptions view with pagination."""
    subscription_list = Subscription.objects.filter(user=request.user).order_by('-joined_at')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(subscription_list, 10)  # Show 10 subscriptions per page
    page_obj = paginator.get_page(page_number)
    context = {
        'subscriptions': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'dashboard/subscriptions.html', context)


@login_required
def referrals(request):
    """User referrals view with pagination."""
    # Get or generate referral code
    if not request.user.referral_code:
        request.user.referral_code = str(uuid.uuid4())[:8].upper()
        request.user.save()
    
    # Generate referral URL
    referral_url = request.build_absolute_uri(
        f'/register/?ref={request.user.referral_code}'
    )
    
    # Get referrals with sorting
    referral_list = Referral.objects.filter(referrer=request.user)
    
    # Handle sorting
    sort_param = request.GET.get('sort', '-date')  # Default to newest first
    if sort_param == 'date':
        referral_list = referral_list.order_by('created_at')
    else:  # '-date' or any other value
        referral_list = referral_list.order_by('-created_at')
    
    # Handle pagination
    paginator = Paginator(referral_list, 10)  # Show 10 referrals per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'referral_url': referral_url,
        'referrals': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'dashboard/referrals.html', context)

@login_required
def notifications(request):
    """User notifications view."""
    notifications = request.user.notifications.all()
    # Mark notifications as read
    notifications.update(read=True)
    context = {
        'notifications': notifications
    }
    return render(request, 'dashboard/notifications.html', context)

@login_required
def withdrawal(request):
    """Withdrawal view."""
    # Get user's wallet and referral bonus balances
    try:
        wallet = request.user.wallet
        wallet_balance = wallet.balance if wallet else Decimal('0.00')
    except:
        wallet_balance = Decimal('0.00')

    try:
        referral_bonus = request.user.referral_bonus_wallet
    except:
        referral_bonus = Decimal('0.00')

    context = {
        'wallet_balance': wallet_balance,
        'referral_bonus': referral_bonus,
    }

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', '0'))
        account_type = request.POST.get('account_type')
        wallet_address = request.POST.get('wallet_address')

        if amount < 25:
            messages.error(request, 'Minimum withdrawal amount is $25')
            return render(request, 'dashboard/withdrawal.html', context)

        # Validate balance based on account type
        if account_type == 'referral_bonus' and amount > referral_bonus:
            messages.error(request, 'Insufficient referral bonus balance')
            return render(request, 'dashboard/withdrawal.html', context)
        elif account_type == 'main_balance' and amount > wallet_balance:
            messages.error(request, 'Insufficient wallet balance')
            return render(request, 'dashboard/withdrawal.html', context)

        try:
            # Create withdrawal request
            withdrawal = Withdrawal.objects.create(
                user=request.user,
                amount=amount,
                withdrawal_type='CRYPTO',
                wallet_address=wallet_address,
                status='PENDING'
            )

            # Create transaction record
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='WITHDRAWAL',
                amount=amount,
                status='PENDING',
                transaction_id=f"WD-{timezone.now().timestamp()}",
                description=f"Withdrawal request for ${amount}"
            )

            # Link transaction to withdrawal
            withdrawal.transaction = transaction
            withdrawal.save()

            messages.success(request, f'Successfully initiated withdrawal of ${amount}')
            return redirect('frontend:dashboard')
        except Exception as e:
            messages.error(request, f'Error processing withdrawal: {str(e)}')
            return render(request, 'dashboard/withdrawal.html', context)

    return render(request, 'dashboard/withdrawal.html', context)

@login_required
def profile(request):
    """User profile view."""
    edit_mode = request.GET.get('edit') == 'true'
    
    if request.method == 'POST':
        user = request.user
        
        # Update basic fields
        user.first_name = request.POST.get('full_name', user.first_name)
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone', user.phone_number)
        
        # Handle image upload
        if 'image' in request.FILES:
            image = request.FILES['image']
            # Validate image
            if image.content_type.startswith('image/'):
                # Delete old image if it exists
                if user.profile_picture:
                    user.profile_picture.delete(save=False)
                user.profile_picture = image
            else:
                messages.error(request, 'Please upload a valid image file.')
                return render(request, 'dashboard/profile.html', {
                    'edit': True,
                    'error': 'Invalid file type. Please upload an image.'
                })
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('frontend:profile')
        except Exception as e:
            messages.error(request, 'An error occurred while updating your profile.')
            return render(request, 'dashboard/profile.html', {
                'edit': True,
                'error': str(e)
            })
            
    return render(request, 'dashboard/profile.html', {
        'edit': edit_mode,
    })

def about(request):
    """About page view."""
    return render(request, 'about.html')

def features(request):
    """Features page view."""
    return render(request, 'features.html')

def contact(request):
    """Contact page view."""
    if request.method == 'POST':
        # Handle contact form submission here
        messages.success(request, 'Message sent successfully!')
        return redirect('contact')
    return render(request, 'contact.html')

def privacy(request):
    """Privacy policy view."""
    return render(request, 'privacy.html')

def terms(request):
    """Terms and conditions view."""
    return render(request, 'terms.html')

def how_it_works(request):
    """How it works view."""
    return render(request, 'how_it_works.html')

@login_required
def submit_payment(request):
    """Handle payment submission."""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed.'
        }, status=405)

    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        amount = Decimal(data.get('amount_paid', '0'))
        transaction_id = data.get('transaction_id', '').strip()
        token_id = data.get('token_id', '').strip()

        # Validate required fields
        if not all([amount, transaction_id, token_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'Please fill in all required fields.'
            }, status=400)

        # Validate amount
        if amount <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Amount must be greater than 0.'
            }, status=400)

        # Check if transaction_id is unique
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Transaction ID already exists.'
            }, status=400)

        # Create new payment record
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            transaction_id=transaction_id,
            token_id=token_id,
            status='pending'
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Payment submitted successfully. Our team will verify your transaction.',
            'payment_id': payment.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data.'
        }, status=400)
    except (ValueError, decimal.InvalidOperation):
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid amount provided.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred. Please try again.'
        }, status=500)

@login_required
def subscribe_plan(request, plan_id):
    """Handle plan subscription."""
    try:
        plan = Plan.objects.get(id=plan_id)
        
        # Check if user already has an active subscription
        if Subscription.objects.filter(user=request.user, status='active').exists():
            messages.error(request, 'You already have an active subscription.')
            return redirect('frontend:dashboard')
            
        # Check if user has sufficient balance
        if request.user.balance < plan.contribution_amount:
            messages.error(request, f'Insufficient balance. Please fund your account with at least ${plan.contribution_amount}.')
            return redirect('frontend:fund_account')
            
        # Create subscription
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='active'
        )
        
        # Deduct the plan price from user's balance
        request.user.balance -= plan.contribution_amount
        request.user.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            amount=-plan.contribution_amount,
            transaction_type='subscription',
            description=f'Subscription to {plan.name} plan'
        )
        
        # Handle referral bonus if user was referred
        if request.user.referred_by:
            bonus_amount = plan.contribution_amount * Decimal('0.05')  # 5% referral bonus
            referral = Referral.objects.get(
                referrer=request.user.referred_by,
                referred_user=request.user
            )
            referral.bonus_amount = bonus_amount
            referral.save()
            
            # Add bonus to referrer's referral bonus wallet
            request.user.referred_by.referral_bonus_wallet += bonus_amount
            request.user.referred_by.save()
            
            # Create transaction record for referral bonus
            Transaction.objects.create(
                user=request.user.referred_by,
                amount=bonus_amount,
                transaction_type='referral_bonus',
                description=f'Referral bonus from {request.user.username}'
            )
            
            # Create notification for referrer
            Notification.objects.create(
                user=request.user.referred_by,
                title='Referral Bonus Received',
                message=f'You received a ${bonus_amount} referral bonus from {request.user.username}',
                notification_type='success'
            )
        
        messages.success(request, f'Successfully subscribed to {plan.name} plan!')
        return redirect('frontend:dashboard')
        
    except Plan.DoesNotExist:
        messages.error(request, 'Invalid plan selected.')
        return redirect('frontend:dashboard')
    except Exception as e:
        messages.error(request, 'An error occurred while processing your subscription.')
        return redirect('frontend:dashboard')
