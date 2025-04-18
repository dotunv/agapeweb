# API Documentation

This document provides comprehensive documentation for the Agape API, including endpoints, request/response formats, and examples.

## Table of Contents

1. [Authentication](#authentication)
2. [Users](#users)
3. [Subscriptions](#subscriptions)
4. [Transactions](#transactions)
5. [Core](#core)

## Authentication

The Agape API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints, you need to include the token in the Authorization header of your requests.

### Endpoints

#### Register a new user

```
POST /api/auth/register/
```

Request body:
```json
{
  "username": "johndoe",
  "email": "john.doe@example.com",
  "password": "securepassword123",
  "password2": "securepassword123"
}
```

Response:
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john.doe@example.com"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Obtain authentication token

```
POST /api/auth/token/
```

Request body:
```json
{
  "email": "john.doe@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh authentication token

```
POST /api/auth/token/refresh/
```

Request body:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Google OAuth login

```
POST /api/auth/google/
```

Request body:
```json
{
  "access_token": "ya29.a0AfH6SMBx5thI-QepA9e..."
}
```

Response:
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john.doe@example.com"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Get user profile

```
GET /api/auth/me/
```

Response:
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john.doe@example.com",
  "referral_code": "ABC123XYZ",
  "pre_starter_wallet": "0.00",
  "starter_wallet": "0.00",
  "basic1_wallet": "0.00",
  "basic2_wallet": "0.00",
  "standard_wallet": "0.00",
  "ultimate1_wallet": "0.00",
  "ultimate2_wallet": "0.00",
  "referral_bonus_wallet": "0.00",
  "funding_wallet": "0.00"
}
```

#### Logout

```
POST /api/auth/logout/
```

Response:
```json
{
  "detail": "Successfully logged out."
}
```

#### Logout all sessions

```
POST /api/auth/logoutall/
```

Response:
```json
{
  "detail": "Successfully logged out from all sessions."
}
```

## Users

The Users API provides endpoints for managing user accounts.

### Endpoints

The Users API shares the same endpoints as the Authentication API:

- `POST /api/users/register/` - Register a new user
- `POST /api/users/token/` - Obtain authentication token
- `POST /api/users/token/refresh/` - Refresh authentication token
- `POST /api/users/google/` - Google OAuth login
- `GET /api/users/me/` - Get user profile

## Subscriptions

The Subscriptions API provides endpoints for managing subscription plans, user subscriptions, contributions, queues, wallets, and referrals.

### Endpoints

#### List all subscription plans

```
GET /api/subscriptions/plans/
```

Response:
```json
[
  {
    "id": 1,
    "name": "Pre-Starter",
    "price": "10.00",
    "description": "Entry-level subscription plan",
    "features": ["Basic support", "Limited access"],
    "duration_days": 30,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Starter",
    "price": "25.00",
    "description": "Starter subscription plan",
    "features": ["Email support", "Full access"],
    "duration_days": 30,
    "is_active": true
  }
]
```

#### Get a specific subscription plan

```
GET /api/subscriptions/plans/{id}/
```

Response:
```json
{
  "id": 1,
  "name": "Pre-Starter",
  "price": "10.00",
  "description": "Entry-level subscription plan",
  "features": ["Basic support", "Limited access"],
  "duration_days": 30,
  "is_active": true
}
```

#### List all user subscriptions

```
GET /api/subscriptions/subscriptions/
```

Response:
```json
[
  {
    "id": 1,
    "user": 1,
    "plan": 1,
    "status": "ACTIVE",
    "start_date": "2023-05-01T00:00:00Z",
    "end_date": "2023-05-31T00:00:00Z",
    "auto_renew": true,
    "created_at": "2023-04-30T12:00:00Z",
    "updated_at": "2023-04-30T12:00:00Z"
  }
]
```

#### Create a new subscription

```
POST /api/subscriptions/subscriptions/
```

Request body:
```json
{
  "plan": 1,
  "auto_renew": true
}
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "plan": 1,
  "status": "PENDING",
  "start_date": "2023-05-01T00:00:00Z",
  "end_date": "2023-05-31T00:00:00Z",
  "auto_renew": true,
  "created_at": "2023-04-30T12:00:00Z",
  "updated_at": "2023-04-30T12:00:00Z"
}
```

#### Get a specific subscription

```
GET /api/subscriptions/subscriptions/{id}/
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "plan": 1,
  "status": "ACTIVE",
  "start_date": "2023-05-01T00:00:00Z",
  "end_date": "2023-05-31T00:00:00Z",
  "auto_renew": true,
  "created_at": "2023-04-30T12:00:00Z",
  "updated_at": "2023-04-30T12:00:00Z"
}
```

#### Update a subscription

```
PUT /api/subscriptions/subscriptions/{id}/
```

Request body:
```json
{
  "auto_renew": false
}
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "plan": 1,
  "status": "ACTIVE",
  "start_date": "2023-05-01T00:00:00Z",
  "end_date": "2023-05-31T00:00:00Z",
  "auto_renew": false,
  "created_at": "2023-04-30T12:00:00Z",
  "updated_at": "2023-05-01T12:00:00Z"
}
```

#### List all contributions

```
GET /api/subscriptions/contributions/
```

Response:
```json
[
  {
    "id": 1,
    "from_subscription": 1,
    "to_subscription": 2,
    "amount": "10.00",
    "created_at": "2023-05-01T12:00:00Z"
  }
]
```

#### List all queues

```
GET /api/subscriptions/queues/
```

Response:
```json
[
  {
    "id": 1,
    "plan": 1,
    "position": 1,
    "subscription": 1,
    "created_at": "2023-05-01T12:00:00Z",
    "updated_at": "2023-05-01T12:00:00Z"
  }
]
```

#### List all wallets

```
GET /api/subscriptions/wallets/
```

Response:
```json
[
  {
    "id": 1,
    "user": 1,
    "wallet_type": "SUBSCRIPTION",
    "plan": 1,
    "balance": "100.00",
    "created_at": "2023-05-01T12:00:00Z",
    "updated_at": "2023-05-01T12:00:00Z"
  }
]
```

#### List all referrals

```
GET /api/subscriptions/referrals/
```

Response:
```json
[
  {
    "id": 1,
    "referrer": 1,
    "referred": 2,
    "subscription": 2,
    "bonus_amount": "5.00",
    "created_at": "2023-05-01T12:00:00Z"
  }
]
```

## Transactions

The Transactions API provides endpoints for managing financial transactions and withdrawal requests.

### Endpoints

#### List all transactions

```
GET /api/transactions/transactions/
```

Response:
```json
[
  {
    "id": 1,
    "user": 1,
    "transaction_type": "DEPOSIT",
    "amount": "100.00",
    "status": "COMPLETED",
    "transaction_id": "txn_123456789",
    "description": "Initial deposit",
    "created_at": "2023-05-01T12:00:00Z",
    "completed_at": "2023-05-01T12:05:00Z"
  }
]
```

#### Get a specific transaction

```
GET /api/transactions/transactions/{id}/
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "transaction_type": "DEPOSIT",
  "amount": "100.00",
  "status": "COMPLETED",
  "transaction_id": "txn_123456789",
  "description": "Initial deposit",
  "created_at": "2023-05-01T12:00:00Z",
  "completed_at": "2023-05-01T12:05:00Z"
}
```

#### List all withdrawals

```
GET /api/transactions/withdrawals/
```

Response:
```json
[
  {
    "id": 1,
    "user": 1,
    "amount": "50.00",
    "status": "PENDING",
    "withdrawal_type": "WALLET",
    "transaction": 2,
    "withdrawal_fee": "2.50",
    "created_at": "2023-05-02T12:00:00Z",
    "processed_at": null,
    "subscription": null,
    "wallet": 1
  }
]
```

#### Create a new withdrawal request

```
POST /api/transactions/withdrawals/
```

Request body:
```json
{
  "amount": "50.00",
  "withdrawal_type": "WALLET",
  "wallet": 1
}
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "amount": "50.00",
  "status": "PENDING",
  "withdrawal_type": "WALLET",
  "transaction": 2,
  "withdrawal_fee": "2.50",
  "created_at": "2023-05-02T12:00:00Z",
  "processed_at": null,
  "subscription": null,
  "wallet": 1
}
```

#### Get a specific withdrawal

```
GET /api/transactions/withdrawals/{id}/
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "amount": "50.00",
  "status": "PENDING",
  "withdrawal_type": "WALLET",
  "transaction": 2,
  "withdrawal_fee": "2.50",
  "created_at": "2023-05-02T12:00:00Z",
  "processed_at": null,
  "subscription": null,
  "wallet": 1
}
```

#### Approve a withdrawal

```
POST /api/transactions/withdrawals/{id}/approve/
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "amount": "50.00",
  "status": "APPROVED",
  "withdrawal_type": "WALLET",
  "transaction": 2,
  "withdrawal_fee": "2.50",
  "created_at": "2023-05-02T12:00:00Z",
  "processed_at": "2023-05-02T12:30:00Z",
  "subscription": null,
  "wallet": 1
}
```

#### Reject a withdrawal

```
POST /api/transactions/withdrawals/{id}/reject/
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "amount": "50.00",
  "status": "REJECTED",
  "withdrawal_type": "WALLET",
  "transaction": 2,
  "withdrawal_fee": "2.50",
  "created_at": "2023-05-02T12:00:00Z",
  "processed_at": "2023-05-02T12:30:00Z",
  "subscription": null,
  "wallet": 1
}
```

## Core

The Core API provides utility endpoints.

### Endpoints

#### Health check

```
GET /api/health/
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2023-05-01T12:00:00Z"
}
```

## API Documentation

The API documentation is available at the following endpoints:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- Raw Schema: `/api/schema/`