from prometheus_client import Counter, Histogram, Gauge
from django.conf import settings

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)

# User Metrics
user_registrations_total = Counter(
    'user_registrations_total',
    'Total number of user registrations'
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

# Subscription Metrics
subscription_creations_total = Counter(
    'subscription_creations_total',
    'Total number of subscription creations',
    ['plan_type']
)

active_subscriptions = Gauge(
    'active_subscriptions',
    'Number of active subscriptions',
    ['plan_type']
)

# Payment Metrics
payment_attempts_total = Counter(
    'payment_attempts_total',
    'Total number of payment attempts',
    ['status']
)

payment_amount_total = Counter(
    'payment_amount_total',
    'Total amount of payments processed',
    ['currency']
)

# Queue Metrics
queue_size = Gauge(
    'queue_size',
    'Current size of the contribution queue',
    ['plan_type']
)

queue_wait_time_seconds = Histogram(
    'queue_wait_time_seconds',
    'Time spent waiting in queue',
    ['plan_type']
)

# System Metrics
system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

# Database Metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

db_connections = Gauge(
    'db_connections',
    'Number of active database connections'
)