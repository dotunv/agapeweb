# User Manual for Admin Interface

This document provides a comprehensive guide for using the Django admin interface to manage the Agape subscription management system.

## Table of Contents

1. [Introduction](#introduction)
2. [Accessing the Admin Interface](#accessing-the-admin-interface)
3. [Dashboard Overview](#dashboard-overview)
4. [User Management](#user-management)
5. [Subscription Management](#subscription-management)
6. [Transaction Management](#transaction-management)
7. [System Configuration](#system-configuration)
8. [Reports and Analytics](#reports-and-analytics)
9. [Troubleshooting](#troubleshooting)

## Introduction

The Agape admin interface is built on Django's powerful admin framework, customized to provide a user-friendly experience for managing the subscription management system. This interface allows administrators to:

- Manage users and their subscriptions
- Configure subscription plans
- Process transactions and withdrawals
- Monitor system performance
- Generate reports and analytics

## Accessing the Admin Interface

### URL

The admin interface is available at:

```
https://your-domain.com/admin/
```

Replace `your-domain.com` with your actual domain name.

### Login Credentials

To access the admin interface, you need administrator credentials. If you don't have these credentials, contact the system administrator or use the superuser account created during deployment.

## Dashboard Overview

After logging in, you'll see the admin dashboard, which provides an overview of the system:

![Admin Dashboard](../images/admin_dashboard.png)

The dashboard is divided into several sections:

1. **Navigation Sidebar**: Access different models and functionalities
2. **Recent Actions**: Shows your recent activities in the admin interface
3. **Quick Links**: Provides shortcuts to common tasks
4. **System Status**: Displays the current status of the system

## User Management

### Viewing Users

To view all users in the system:

1. Click on "Users" in the "Authentication and Authorization" section
2. You'll see a list of all users with their username, email, and status

### Creating a New User

To create a new user:

1. Click on "Users" in the "Authentication and Authorization" section
2. Click the "Add User" button in the top right corner
3. Enter the username and password for the new user
4. Click "Save and continue editing"
5. Fill in additional details such as:
   - Personal info (first name, last name, email)
   - Permissions
   - Wallet balances
   - Referral information
6. Click "Save" to create the user

### Editing a User

To edit an existing user:

1. Click on "Users" in the "Authentication and Authorization" section
2. Find the user you want to edit and click on their username
3. Update the user's information
4. Click "Save" to apply the changes

### Deactivating a User

To deactivate a user without deleting their account:

1. Click on "Users" in the "Authentication and Authorization" section
2. Find the user you want to deactivate and click on their username
3. Uncheck the "Active" checkbox in the "Permissions" section
4. Click "Save" to apply the changes

### Deleting a User

To delete a user:

1. Click on "Users" in the "Authentication and Authorization" section
2. Find the user you want to delete and select the checkbox next to their username
3. Select "Delete selected users" from the action dropdown
4. Click "Go" to confirm the action
5. Confirm the deletion on the confirmation page

**Note**: Deleting a user will also delete all related data, including subscriptions, transactions, and wallet balances. Consider deactivating the user instead if you want to preserve their data.

## Subscription Management

### Viewing Subscription Plans

To view all subscription plans:

1. Click on "Plans" in the "Subscriptions" section
2. You'll see a list of all plans with their name, price, and status

### Creating a New Subscription Plan

To create a new subscription plan:

1. Click on "Plans" in the "Subscriptions" section
2. Click the "Add Plan" button in the top right corner
3. Fill in the plan details:
   - Name
   - Price
   - Description
   - Features (as a JSON list)
   - Duration in days
   - Active status
4. Click "Save" to create the plan

### Editing a Subscription Plan

To edit an existing subscription plan:

1. Click on "Plans" in the "Subscriptions" section
2. Find the plan you want to edit and click on its name
3. Update the plan's information
4. Click "Save" to apply the changes

**Note**: Editing a plan will affect all users who are currently subscribed to that plan. Consider creating a new plan instead if you want to make significant changes.

### Viewing User Subscriptions

To view all user subscriptions:

1. Click on "Subscriptions" in the "Subscriptions" section
2. You'll see a list of all subscriptions with their user, plan, status, and dates

### Creating a New Subscription

To create a new subscription for a user:

1. Click on "Subscriptions" in the "Subscriptions" section
2. Click the "Add Subscription" button in the top right corner
3. Fill in the subscription details:
   - User
   - Plan
   - Status
   - Start date
   - End date
   - Auto-renew option
4. Click "Save" to create the subscription

### Managing the Queue

To manage the subscription queue:

1. Click on "Queues" in the "Subscriptions" section
2. You'll see a list of all queues with their plan, position, and subscription
3. To add a subscription to the queue, click the "Add Queue" button
4. To shift the queue, select the queue entries and choose "Shift selected queues" from the action dropdown

## Transaction Management

### Viewing Transactions

To view all transactions:

1. Click on "Transactions" in the "Transactions" section
2. You'll see a list of all transactions with their user, type, amount, and status

### Creating a New Transaction

To create a new transaction:

1. Click on "Transactions" in the "Transactions" section
2. Click the "Add Transaction" button in the top right corner
3. Fill in the transaction details:
   - User
   - Transaction type
   - Amount
   - Status
   - Transaction ID
   - Description
4. Click "Save" to create the transaction

### Managing Withdrawals

To manage withdrawal requests:

1. Click on "Withdrawals" in the "Transactions" section
2. You'll see a list of all withdrawals with their user, amount, status, and type
3. To approve a withdrawal:
   - Click on the withdrawal
   - Click the "Approve" button at the bottom of the page
4. To reject a withdrawal:
   - Click on the withdrawal
   - Click the "Reject" button at the bottom of the page

## System Configuration

### Managing Site Settings

To manage site-wide settings:

1. Click on "Sites" in the "Sites" section
2. Click on the site you want to edit
3. Update the domain name and display name
4. Click "Save" to apply the changes

### Managing Email Templates

If you're using custom email templates:

1. Click on "Email templates" in the "Email" section
2. You'll see a list of all email templates
3. Click on a template to edit it
4. Update the subject, content, and HTML version
5. Click "Save" to apply the changes

## Reports and Analytics

### Generating Reports

To generate reports:

1. Click on "Reports" in the "Reports" section
2. Select the type of report you want to generate
3. Set the date range and other filters
4. Click "Generate Report"
5. The report will be displayed and can be exported as CSV or PDF

### Viewing Analytics

To view system analytics:

1. Click on "Analytics" in the "Reports" section
2. You'll see various charts and graphs showing:
   - User growth
   - Subscription trends
   - Transaction volume
   - Revenue metrics
3. Use the filters to adjust the time period and other parameters

## Troubleshooting

### Common Issues

#### User Can't Log In

1. Check if the user account is active
2. Verify that the user has the correct permissions
3. Reset the user's password if necessary

#### Subscription Not Processing

1. Check if the subscription is active
2. Verify that the subscription dates are correct
3. Check if the user has sufficient funds in their wallet

#### Transaction Failed

1. Check the transaction status and error message
2. Verify that the user has sufficient funds
3. Check for any system-wide issues that might affect transactions

### Getting Help

If you encounter issues that aren't covered in this manual:

1. Check the [Troubleshooting Guide](../troubleshooting/README.md) for more detailed solutions
2. Contact the system administrator or development team
3. Submit a support ticket through the support system

### Logging Issues

To help with troubleshooting, always include:

1. The specific action you were trying to perform
2. Any error messages you received
3. The user account affected (if applicable)
4. The date and time when the issue occurred
5. Screenshots of the issue (if possible)