from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            
            # Check if account is locked
            if user.is_account_locked():
                raise ValidationError('Account is temporarily locked due to too many failed login attempts.')
            
            # Verify password
            if user.check_password(password):
                # Reset failed login attempts on successful login
                user.reset_failed_logins()
                return user
            else:
                # Increment failed login attempts
                user.increment_failed_login()
                return None
                
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 