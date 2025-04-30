from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib import messages

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the current URL is in the admin namespace
        try:
            resolved = resolve(request.path)
            is_admin_url = resolved.namespace == 'admin'
        except:
            is_admin_url = False

        if is_admin_url:
            # Check if user is authenticated and is staff
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in with admin credentials to access this area.')
                return redirect(f"{reverse('admin:login')}?next={request.path}")
            
            if not request.user.is_staff:
                messages.error(request, 'You do not have permission to access the admin area.')
                return redirect('frontend:dashboard')

            # Add security headers for admin pages
            response = self.get_response(request)
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            response['Referrer-Policy'] = 'strict-origin-same-origin'
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            return response

        return self.get_response(request) 