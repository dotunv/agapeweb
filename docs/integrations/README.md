# Third-Party Integrations

This document provides detailed information about the external services integrated with the Agape subscription management system, including configuration, usage, and troubleshooting.

## Table of Contents

1. [Overview](#overview)
2. [Authentication Integrations](#authentication-integrations)
3. [Payment Integrations](#payment-integrations)
4. [Communication Integrations](#communication-integrations)
5. [Analytics Integrations](#analytics-integrations)
6. [Monitoring Integrations](#monitoring-integrations)
7. [Integration Best Practices](#integration-best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

The Agape subscription management system integrates with various third-party services to provide a complete solution. These integrations are implemented using a consistent pattern:

1. **Service Abstraction**: Each integration is abstracted behind a service interface
2. **Configuration Management**: Integration settings are stored in environment variables
3. **Error Handling**: Robust error handling with fallback mechanisms
4. **Logging**: Comprehensive logging of integration activities
5. **Monitoring**: Performance and availability monitoring

## Authentication Integrations

### Google OAuth

The system integrates with Google OAuth for user authentication.

#### Configuration

Configure Google OAuth in your `.env` file:

```
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
GOOGLE_OAUTH_REDIRECT_URI=https://your-domain.com/api/auth/google/callback
```

#### Setup Instructions

1. Create a project in the [Google Developer Console](https://console.developers.google.com/)
2. Enable the Google OAuth API
3. Create OAuth 2.0 credentials
4. Configure the authorized redirect URIs
5. Copy the client ID and client secret to your `.env` file

#### Usage

The Google OAuth integration is used in the following components:

- `users/views.py`: `GoogleLoginView` handles the OAuth login process
- `users/serializers.py`: `GoogleLoginSerializer` validates the OAuth token

Example code for initiating Google OAuth:

```python
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_REDIRECT_URI
    client_class = OAuth2Client
```

#### Troubleshooting

Common issues:

1. **Invalid redirect URI**: Ensure the redirect URI in your Google Developer Console matches the one in your `.env` file
2. **Invalid client ID or secret**: Verify your credentials
3. **User not found**: Ensure the user's email domain is allowed in your Google Developer Console settings

## Payment Integrations

### Stripe

The system integrates with Stripe for payment processing.

#### Configuration

Configure Stripe in your `.env` file:

```
STRIPE_PUBLIC_KEY=your-public-key
STRIPE_SECRET_KEY=your-secret-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret
```

#### Setup Instructions

1. Create a [Stripe account](https://stripe.com/)
2. Get your API keys from the Stripe Dashboard
3. Configure webhook endpoints
4. Copy the API keys and webhook secret to your `.env` file

#### Usage

The Stripe integration is used in the following components:

- `subscriptions/services.py`: `PaymentService` handles payment processing
- `subscriptions/views.py`: `PaymentWebhookView` handles Stripe webhooks

Example code for processing a payment:

```python
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def process_payment(user, amount, description):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            description=description,
            customer=user.stripe_customer_id,
            metadata={"user_id": user.id}
        )
        return {
            "status": "success",
            "payment_intent_id": payment_intent.id,
            "client_secret": payment_intent.client_secret
        }
    except stripe.error.StripeError as e:
        # Handle error
        return {
            "status": "error",
            "message": str(e)
        }
```

#### Webhooks

Stripe webhooks are used to handle asynchronous payment events:

1. **payment_intent.succeeded**: Update subscription status to active
2. **payment_intent.payment_failed**: Handle failed payments
3. **customer.subscription.updated**: Update subscription details

Example webhook handler:

```python
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment(payment_intent)
    
    return HttpResponse(status=200)
```

#### Troubleshooting

Common issues:

1. **Invalid API keys**: Verify your Stripe API keys
2. **Webhook signature verification failed**: Ensure your webhook secret is correct
3. **Payment declined**: Check the Stripe Dashboard for detailed error messages
4. **Currency mismatch**: Ensure you're using the correct currency code

### PayPal

The system also integrates with PayPal as an alternative payment method.

#### Configuration

Configure PayPal in your `.env` file:

```
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret
PAYPAL_MODE=sandbox  # or 'live' for production
```

#### Setup Instructions

1. Create a [PayPal Developer account](https://developer.paypal.com/)
2. Create a new application
3. Get your client ID and secret
4. Configure webhook endpoints
5. Copy the client ID and secret to your `.env` file

#### Usage

The PayPal integration is used in the following components:

- `subscriptions/services.py`: `PayPalService` handles PayPal payments
- `subscriptions/views.py`: `PayPalWebhookView` handles PayPal webhooks

Example code for creating a PayPal order:

```python
import paypalrestsdk
from django.conf import settings

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def create_paypal_order(user, amount, description):
    try:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "description": description
            }],
            "redirect_urls": {
                "return_url": "https://your-domain.com/payment/success",
                "cancel_url": "https://your-domain.com/payment/cancel"
            }
        })
        
        if payment.create():
            return {
                "status": "success",
                "payment_id": payment.id,
                "approval_url": next(link.href for link in payment.links if link.rel == "approval_url")
            }
        else:
            return {
                "status": "error",
                "message": payment.error
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

#### Troubleshooting

Common issues:

1. **Invalid credentials**: Verify your PayPal client ID and secret
2. **Sandbox vs. Production**: Ensure you're using the correct mode
3. **Currency issues**: Verify that the currency is supported by PayPal
4. **Webhook validation**: Check PayPal webhook logs for delivery issues

## Communication Integrations

### SendGrid

The system integrates with SendGrid for email communications.

#### Configuration

Configure SendGrid in your `.env` file:

```
SENDGRID_API_KEY=your-api-key
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

#### Setup Instructions

1. Create a [SendGrid account](https://sendgrid.com/)
2. Create an API key with mail send permissions
3. Verify your sender domain
4. Copy the API key to your `.env` file

#### Usage

The SendGrid integration is used in the following components:

- `core/services.py`: `EmailService` handles email sending
- `users/services.py`: `UserNotificationService` sends user-specific emails

Example code for sending an email:

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

def send_email(to_email, subject, html_content):
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return {
            "status": "success",
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

#### Email Templates

The system uses the following email templates:

1. **Welcome Email**: Sent when a user registers
2. **Password Reset**: Sent when a user requests a password reset
3. **Subscription Confirmation**: Sent when a subscription is created
4. **Withdrawal Approval**: Sent when a withdrawal is approved
5. **Withdrawal Rejection**: Sent when a withdrawal is rejected

#### Troubleshooting

Common issues:

1. **Invalid API key**: Verify your SendGrid API key
2. **Sender verification**: Ensure your sender domain is verified
3. **Email deliverability**: Check SendGrid's Activity Feed for delivery issues
4. **Rate limiting**: Monitor your SendGrid usage to avoid rate limits

### Twilio

The system integrates with Twilio for SMS notifications.

#### Configuration

Configure Twilio in your `.env` file:

```
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```

#### Setup Instructions

1. Create a [Twilio account](https://www.twilio.com/)
2. Get your Account SID and Auth Token
3. Purchase a phone number
4. Copy the credentials to your `.env` file

#### Usage

The Twilio integration is used in the following components:

- `core/services.py`: `SMSService` handles SMS sending
- `users/services.py`: `UserNotificationService` sends user-specific SMS

Example code for sending an SMS:

```python
from twilio.rest import Client
from django.conf import settings

def send_sms(to_phone, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        return {
            "status": "success",
            "message_sid": message.sid
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

#### SMS Templates

The system uses the following SMS templates:

1. **Verification Code**: Sent for two-factor authentication
2. **Subscription Notification**: Sent when a subscription status changes
3. **Withdrawal Notification**: Sent when a withdrawal is processed

#### Troubleshooting

Common issues:

1. **Invalid credentials**: Verify your Twilio Account SID and Auth Token
2. **Phone number format**: Ensure phone numbers are in E.164 format
3. **Messaging service**: Check Twilio logs for delivery issues
4. **Rate limiting**: Monitor your Twilio usage to avoid rate limits

## Analytics Integrations

### Google Analytics

The system integrates with Google Analytics for user behavior tracking.

#### Configuration

Configure Google Analytics in your `.env` file:

```
GA_TRACKING_ID=your-tracking-id
```

#### Setup Instructions

1. Create a [Google Analytics account](https://analytics.google.com/)
2. Create a property and get your tracking ID
3. Copy the tracking ID to your `.env` file

#### Usage

The Google Analytics integration is used in the following components:

- Frontend applications: Tracking code is included in the HTML templates
- Backend API: Custom events are tracked using the measurement protocol

Example code for tracking a custom event:

```python
import requests
from django.conf import settings
import uuid

def track_event(user_id, category, action, label=None, value=None):
    client_id = user_id or str(uuid.uuid4())
    
    data = {
        'v': '1',
        't': 'event',
        'tid': settings.GA_TRACKING_ID,
        'cid': client_id,
        'ec': category,
        'ea': action
    }
    
    if label:
        data['el'] = label
    
    if value:
        data['ev'] = value
    
    try:
        response = requests.post(
            'https://www.google-analytics.com/collect',
            data=data
        )
        return {
            "status": "success",
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

#### Tracked Events

The system tracks the following events:

1. **User Registration**: When a user registers
2. **User Login**: When a user logs in
3. **Subscription Creation**: When a subscription is created
4. **Payment**: When a payment is processed
5. **Withdrawal**: When a withdrawal is requested

#### Troubleshooting

Common issues:

1. **Invalid tracking ID**: Verify your Google Analytics tracking ID
2. **Ad blockers**: Be aware that some users may have ad blockers that block Google Analytics
3. **Data processing delay**: Google Analytics data may take up to 24 hours to process
4. **Sampling**: Large volumes of data may be sampled in reports

## Monitoring Integrations

### Sentry

The system integrates with Sentry for error tracking and performance monitoring.

#### Configuration

Configure Sentry in your `.env` file:

```
SENTRY_DSN=your-sentry-dsn
```

#### Setup Instructions

1. Create a [Sentry account](https://sentry.io/)
2. Create a new project
3. Get your DSN
4. Copy the DSN to your `.env` file

#### Usage

The Sentry integration is used throughout the application to track errors and performance issues.

Example code for configuring Sentry:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from django.conf import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)
```

#### Tracked Issues

Sentry tracks the following types of issues:

1. **Exceptions**: Unhandled exceptions in the application
2. **Performance Issues**: Slow API endpoints and database queries
3. **Frontend Errors**: JavaScript errors in the frontend application
4. **API Errors**: HTTP 4xx and 5xx responses

#### Troubleshooting

Common issues:

1. **Invalid DSN**: Verify your Sentry DSN
2. **Rate limiting**: Monitor your Sentry usage to avoid rate limits
3. **PII data**: Ensure sensitive data is not being sent to Sentry
4. **Event filtering**: Configure Sentry to filter out noisy events

### New Relic

The system integrates with New Relic for application performance monitoring.

#### Configuration

Configure New Relic in your `.env` file:

```
NEW_RELIC_LICENSE_KEY=your-license-key
NEW_RELIC_APP_NAME=your-app-name
```

#### Setup Instructions

1. Create a [New Relic account](https://newrelic.com/)
2. Create a new application
3. Get your license key
4. Copy the license key to your `.env` file

#### Usage

The New Relic integration is used to monitor application performance.

Example code for configuring New Relic:

```python
# newrelic.ini
[newrelic]
license_key = <%= ENV['NEW_RELIC_LICENSE_KEY'] %>
app_name = <%= ENV['NEW_RELIC_APP_NAME'] %>
monitor_mode = true
log_level = info
ssl = true
transaction_tracer.enabled = true
transaction_tracer.transaction_threshold = apdex_f
transaction_tracer.record_sql = obfuscated
transaction_tracer.stack_trace_threshold = 0.5
transaction_tracer.explain_enabled = true
transaction_tracer.explain_threshold = 0.5
error_collector.enabled = true
browser_monitoring.auto_instrument = true
```

#### Monitored Metrics

New Relic monitors the following metrics:

1. **Response Time**: Average response time for API endpoints
2. **Throughput**: Requests per minute
3. **Error Rate**: Percentage of requests that result in errors
4. **Database Performance**: Query execution time
5. **External Services**: Response time for external API calls

#### Troubleshooting

Common issues:

1. **Invalid license key**: Verify your New Relic license key
2. **Agent not reporting**: Check that the New Relic agent is properly installed
3. **Missing data**: Ensure that the application is generating enough traffic to report metrics
4. **Configuration issues**: Verify your New Relic configuration

## Integration Best Practices

### Security

1. **Store credentials securely**: Use environment variables or a secrets manager
2. **Limit permissions**: Use the principle of least privilege for API keys
3. **Rotate credentials**: Regularly rotate API keys and secrets
4. **Monitor usage**: Watch for unusual activity that might indicate a breach
5. **Validate webhooks**: Verify webhook signatures to prevent spoofing

### Reliability

1. **Implement retries**: Use exponential backoff for failed requests
2. **Circuit breakers**: Prevent cascading failures when services are down
3. **Fallback mechanisms**: Have alternative paths when integrations fail
4. **Monitoring**: Set up alerts for integration failures
5. **Testing**: Regularly test integrations with mock services

### Performance

1. **Asynchronous processing**: Use background tasks for non-critical operations
2. **Caching**: Cache responses from third-party services when appropriate
3. **Batch operations**: Combine multiple operations into a single request when possible
4. **Rate limiting**: Respect and implement rate limits to avoid throttling
5. **Monitoring**: Track performance metrics for all integrations

## Troubleshooting

### General Troubleshooting Steps

1. **Check logs**: Review application logs for error messages
2. **Verify credentials**: Ensure API keys and secrets are correct
3. **Check service status**: Verify that the third-party service is operational
4. **Test connectivity**: Ensure network connectivity to the service
5. **Review documentation**: Check for changes in the service's API

### Common Integration Issues

1. **Authentication failures**: Invalid or expired credentials
2. **Rate limiting**: Exceeding the service's rate limits
3. **API changes**: The service's API has changed
4. **Network issues**: Connectivity problems between your application and the service
5. **Configuration errors**: Misconfigured integration settings

### Getting Help

If you encounter issues with third-party integrations:

1. **Check service status**: Visit the service's status page
2. **Review documentation**: Check the service's documentation for updates
3. **Contact support**: Reach out to the service's support team
4. **Community forums**: Ask for help in community forums
5. **Internal documentation**: Check internal documentation for known issues and solutions