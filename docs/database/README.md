# Database Schema and Relationships

This document provides a comprehensive overview of the database schema used in the Agape subscription management system, including models, fields, and relationships between them.

## Table of Contents

1. [Overview](#overview)
2. [Users](#users)
3. [Subscriptions](#subscriptions)
4. [Transactions](#transactions)
5. [Entity Relationship Diagram](#entity-relationship-diagram)

## Overview

The Agape database schema is organized into three main components:

1. **Users**: Manages user accounts, authentication, and user-specific data
2. **Subscriptions**: Handles subscription plans, user subscriptions, queues, wallets, and referrals
3. **Transactions**: Tracks financial transactions and withdrawal requests

## Users

### User Model

The `User` model extends Django's `AbstractUser` and adds additional fields for the subscription management system.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| username | CharField | Single word containing only letters and numbers |
| email | EmailField | User's email address (used for authentication) |
| referral_code | CharField | Unique 10-character code for referrals |
| referred_by | ForeignKey | Reference to the user who referred this user |
| google_id | CharField | Google OAuth ID for authentication |
| profile_picture | URLField | URL to user's profile picture |
| pre_starter_wallet | DecimalField | Balance in pre-starter wallet |
| starter_wallet | DecimalField | Balance in starter wallet |
| basic1_wallet | DecimalField | Balance in basic1 wallet |
| basic2_wallet | DecimalField | Balance in basic2 wallet |
| standard_wallet | DecimalField | Balance in standard wallet |
| ultimate1_wallet | DecimalField | Balance in ultimate1 wallet |
| ultimate2_wallet | DecimalField | Balance in ultimate2 wallet |
| referral_bonus_wallet | DecimalField | Balance in referral bonus wallet |
| funding_wallet | DecimalField | Balance in funding wallet |

**Methods:**

- `generate_referral_code()`: Generates a unique 10-character referral code
- `save()`: Overrides the save method to generate a referral code if one doesn't exist

**Relationships:**

- `referred_by`: Many-to-one relationship with itself (User can refer multiple users)
- `referrals`: One-to-many relationship with itself (reverse of referred_by)

## Subscriptions

### Plan Model

The `Plan` model represents subscription plans available in the system.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | CharField | Name of the plan |
| price | DecimalField | Price of the plan |
| description | TextField | Description of the plan |
| features | JSONField | List of features included in the plan |
| duration_days | IntegerField | Duration of the plan in days |
| is_active | BooleanField | Whether the plan is active |

**Relationships:**

- `subscriptions`: One-to-many relationship with Subscription model

### Subscription Model

The `Subscription` model represents a user's subscription to a plan.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey | Reference to the user who owns the subscription |
| plan | ForeignKey | Reference to the subscription plan |
| status | CharField | Status of the subscription (PENDING, ACTIVE, EXPIRED, CANCELLED) |
| start_date | DateTimeField | Start date of the subscription |
| end_date | DateTimeField | End date of the subscription |
| auto_renew | BooleanField | Whether the subscription should auto-renew |
| created_at | DateTimeField | When the subscription was created |
| updated_at | DateTimeField | When the subscription was last updated |

**Methods:**

- `process_payment(from_subscription, amount)`: Processes a payment from another subscription
- `request_withdrawal(amount)`: Requests a withdrawal from the subscription

**Relationships:**

- `user`: Many-to-one relationship with User model
- `plan`: Many-to-one relationship with Plan model
- `contributions_made`: One-to-many relationship with Contribution model (as from_subscription)
- `contributions_received`: One-to-many relationship with Contribution model (as to_subscription)
- `queue_position`: One-to-one relationship with Queue model
- `withdrawals`: One-to-many relationship with Withdrawal model

### Contribution Model

The `Contribution` model represents a contribution from one subscription to another.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| from_subscription | ForeignKey | Reference to the subscription making the contribution |
| to_subscription | ForeignKey | Reference to the subscription receiving the contribution |
| amount | DecimalField | Amount of the contribution |
| created_at | DateTimeField | When the contribution was made |

**Relationships:**

- `from_subscription`: Many-to-one relationship with Subscription model
- `to_subscription`: Many-to-one relationship with Subscription model

### Queue Model

The `Queue` model manages the queue system for subscriptions.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| plan | ForeignKey | Reference to the subscription plan |
| position | IntegerField | Position in the queue |
| subscription | OneToOneField | Reference to the subscription in the queue |
| created_at | DateTimeField | When the queue entry was created |
| updated_at | DateTimeField | When the queue entry was last updated |

**Methods:**

- `shift_queue()`: Shifts the queue when a subscription is processed
- `add_to_queue(subscription)`: Adds a subscription to the queue

**Relationships:**

- `plan`: Many-to-one relationship with Plan model
- `subscription`: One-to-one relationship with Subscription model

### Wallet Model

The `Wallet` model manages financial transactions for users.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey | Reference to the user who owns the wallet |
| wallet_type | CharField | Type of wallet (SUBSCRIPTION, REFERRAL, FUNDING) |
| plan | ForeignKey | Reference to the subscription plan (for SUBSCRIPTION wallets) |
| balance | DecimalField | Current balance in the wallet |
| created_at | DateTimeField | When the wallet was created |
| updated_at | DateTimeField | When the wallet was last updated |

**Methods:**

- `get_or_create_wallet(user, wallet_type, plan)`: Gets or creates a wallet for a user
- `deposit(amount, description)`: Deposits funds into the wallet
- `withdraw(amount, description)`: Withdraws funds from the wallet

**Relationships:**

- `user`: Many-to-one relationship with User model
- `plan`: Many-to-one relationship with Plan model
- `withdrawals`: One-to-many relationship with Withdrawal model

### Referral Model

The `Referral` model handles referral relationships and bonuses.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| referrer | ForeignKey | Reference to the user who made the referral |
| referred | ForeignKey | Reference to the user who was referred |
| subscription | ForeignKey | Reference to the subscription created through the referral |
| bonus_amount | DecimalField | Amount of the referral bonus |
| created_at | DateTimeField | When the referral was created |

**Methods:**

- `create_referral_bonus(subscription)`: Creates a referral bonus for a subscription

**Relationships:**

- `referrer`: Many-to-one relationship with User model
- `referred`: Many-to-one relationship with User model
- `subscription`: Many-to-one relationship with Subscription model

## Transactions

### Transaction Model

The `Transaction` model represents a financial transaction in the system.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey | Reference to the user who owns the transaction |
| transaction_type | CharField | Type of transaction (DEPOSIT, WITHDRAWAL, REFERRAL_BONUS, SUBSCRIPTION_PAYMENT, QUEUE_PAYMENT) |
| amount | DecimalField | Amount of the transaction |
| status | CharField | Status of the transaction (PENDING, COMPLETED, FAILED, CANCELLED) |
| transaction_id | CharField | Unique identifier for the transaction |
| description | TextField | Description of the transaction |
| created_at | DateTimeField | When the transaction was created |
| completed_at | DateTimeField | When the transaction was completed |

**Relationships:**

- `user`: Many-to-one relationship with User model
- `withdrawal`: One-to-one relationship with Withdrawal model

### Withdrawal Model

The `Withdrawal` model handles withdrawal requests from users.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey | Reference to the user who requested the withdrawal |
| amount | DecimalField | Amount of the withdrawal |
| status | CharField | Status of the withdrawal (PENDING, APPROVED, REJECTED, COMPLETED) |
| withdrawal_type | CharField | Type of withdrawal (SUBSCRIPTION, WALLET, REFERRAL) |
| transaction | OneToOneField | Reference to the transaction associated with the withdrawal |
| withdrawal_fee | DecimalField | Fee applied to the withdrawal (5% of amount) |
| created_at | DateTimeField | When the withdrawal was created |
| processed_at | DateTimeField | When the withdrawal was processed |
| subscription | ForeignKey | Reference to the subscription (for SUBSCRIPTION withdrawals) |
| wallet | ForeignKey | Reference to the wallet (for WALLET withdrawals) |

**Methods:**

- `approve()`: Approves the withdrawal request
- `reject()`: Rejects the withdrawal request and refunds the amount

**Relationships:**

- `user`: Many-to-one relationship with User model
- `transaction`: One-to-one relationship with Transaction model
- `subscription`: Many-to-one relationship with Subscription model
- `wallet`: Many-to-one relationship with Wallet model

## Entity Relationship Diagram

Below is a simplified entity relationship diagram showing the main models and their relationships:

```
+-------+       +---------------+       +-------------+
| User  |------>| Subscription  |------>| Plan        |
+-------+       +---------------+       +-------------+
    |                 |   |                    |
    |                 |   |                    |
    v                 v   v                    v
+-------+       +---------------+       +-------------+
| Wallet |<------| Contribution |<------| Queue       |
+-------+       +---------------+       +-------------+
    |                                         |
    |                                         |
    v                                         v
+---------------+                      +-------------+
| Transaction   |<---------------------| Referral    |
+---------------+                      +-------------+
    |
    |
    v
+---------------+
| Withdrawal    |
+---------------+
```

This diagram shows the main relationships between the models:

- A User can have multiple Subscriptions
- A Subscription belongs to a Plan
- A Subscription can make and receive Contributions
- A Subscription can be in a Queue
- A User can have multiple Wallets
- A Wallet can have multiple Transactions
- A Transaction can be associated with a Withdrawal
- A User can make and receive Referrals

For more detailed information about database migrations and versioning, see [Database Migrations Versioning Strategy](../migrations.md).