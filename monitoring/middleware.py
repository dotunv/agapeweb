import time
from django.conf import settings
from prometheus_client import Counter, Histogram
from .metrics import (
    api_requests_total,
    api_request_duration_seconds,
    db_query_duration_seconds,
)

class MonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timing the request
        start_time = time.time()

        # Process the request
        response = self.get_response(request)

        # Calculate request duration
        duration = time.time() - start_time

        # Record metrics
        api_requests_total.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()

        api_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)

        return response

class DatabaseMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timing database operations
        start_time = time.time()

        # Process the request
        response = self.get_response(request)

        # Calculate database operation duration
        duration = time.time() - start_time

        # Record database metrics
        db_query_duration_seconds.labels(
            operation='request'
        ).observe(duration)

        return response 