from django import forms
from .models import Withdrawal

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['amount', 'withdrawal_type', 'wallet']
        
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        wallet = cleaned_data.get('wallet')
        
        if amount and wallet:
            if amount > wallet.balance:
                raise forms.ValidationError("Insufficient funds in wallet")
            
            # Calculate 5% withdrawal fee
            cleaned_data['withdrawal_fee'] = amount * 0.05
            
        return cleaned_data 