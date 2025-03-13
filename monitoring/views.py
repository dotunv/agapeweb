from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import sentry_sdk
from sentry_sdk import capture_message, set_user, set_context

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def test_sentry(request):
    """Test view to demonstrate Sentry integration"""
    try:
        # Test basic error capture
        result = 1 / 0
    except Exception as e:
        # Capture the error with custom context
        sentry_sdk.set_context("test_context", {
            "test_value": "This is a test error",
            "request_path": request.path,
            "user_agent": request.META.get('HTTP_USER_AGENT')
        })
        raise

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_user_context(request):
    """Test view to demonstrate user context in Sentry"""
    try:
        # Set user context
        set_user({
            "id": request.user.id,
            "email": request.user.email,
            "username": request.user.username,
        })
        
        # Add custom context
        set_context("user_preferences", {
            "theme": "dark",
            "language": "en",
            "timezone": "UTC"
        })
        
        # Test a custom message
        capture_message("User accessed test endpoint", level="info")
        
        return JsonResponse({
            "message": "User context test completed",
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email
            }
        })
    except Exception as e:
        # Capture any errors with user context
        sentry_sdk.set_context("error_context", {
            "user_id": request.user.id if request.user.is_authenticated else None,
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        raise

@api_view(['GET'])
@permission_classes([AllowAny])
def test_performance(request):
    """Test view to demonstrate performance monitoring"""
    try:
        with sentry_sdk.start_transaction(op="test", name="test_performance"):
            # Simulate some work
            import time
            time.sleep(0.1)  # Simulate 100ms of work
            
            # Add performance data
            sentry_sdk.set_context("performance", {
                "operation": "test_performance",
                "duration": 0.1,
                "timestamp": time.time()
            })
            
            return JsonResponse({
                "message": "Performance test completed",
                "duration": 0.1,
                "timestamp": time.time()
            })
    except Exception as e:
        # Capture performance-related errors
        sentry_sdk.set_context("performance_error", {
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        raise
