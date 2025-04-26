from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        Override to customize the login redirect URL.
        """
        # Get the 'next' parameter from the request if it exists
        next_url = request.GET.get('next')
        if next_url:
            return resolve_url(next_url)
        # Otherwise use the default LOGIN_REDIRECT_URL from settings
        return resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_logout_redirect_url(self, request):
        """
        Override to customize the logout redirect URL.
        """
        return resolve_url(settings.LOGOUT_REDIRECT_URL)

    def get_signup_redirect_url(self, request):
        """
        Override to customize the signup redirect URL.
        """
        # After signup, redirect to dashboard
        return resolve_url('frontend:dashboard')

    def is_open_for_signup(self, request):
        """
        Override to control whether signups are allowed.
        """
        return getattr(settings, 'ACCOUNT_ALLOW_SIGNUPS', True) 