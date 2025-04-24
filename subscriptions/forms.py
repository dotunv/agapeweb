from django import forms
from .models import Subscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = []  # No fields needed as they are set in the view
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The form doesn't need any fields because:
        # - user is set from request.user
        # - plan is passed from the URL
        # - status is set to 'PENDING'
        # - other fields are managed by the system 