from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomSignupForm(SignupForm):
    referral_code = forms.CharField(
        max_length=10,
        required=False,
        label=_('Referral Code'),
        help_text=_('Enter a referral code if you were invited by another user'),
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Referral Code (Optional)',
            'class': 'form-input'
        })
    )

    def clean_referral_code(self):
        referral_code = self.cleaned_data.get('referral_code')
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                if referrer == self.user:
                    raise forms.ValidationError(_('You cannot use your own referral code'))
            except User.DoesNotExist:
                raise forms.ValidationError(_('Invalid referral code'))
        return referral_code

    def save(self, request):
        user = super().save(request)
        
        # Handle referral code if provided
        referral_code = self.cleaned_data.get('referral_code')
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                user.referred_by = referrer
                user.save()
            except User.DoesNotExist:
                pass
                
        return user

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    referral_code = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'referral_code')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Handle referral code if provided
            referral_code = self.cleaned_data.get('referral_code')
            if referral_code:
                try:
                    referrer = User.objects.get(referral_code=referral_code)
                    user.referred_by = referrer
                    user.save()
                except User.DoesNotExist:
                    pass
                
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture') 