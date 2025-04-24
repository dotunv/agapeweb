from django import forms
from .models import Withdrawal

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['amount', 'withdrawal_type', 'wallet_address', 'bank_details']
        widgets = {
            'bank_details': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter your bank account details (Account number, Bank name, etc.)'
            }),
            'wallet_address': forms.TextInput(attrs={
                'placeholder': 'Enter your cryptocurrency wallet address'
            })
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        withdrawal_type = cleaned_data.get('withdrawal_type')
        wallet_address = cleaned_data.get('wallet_address')
        bank_details = cleaned_data.get('bank_details')

        if withdrawal_type == 'CRYPTO' and not wallet_address:
            raise forms.ValidationError({
                'wallet_address': "Wallet address is required for crypto withdrawals"
            })
        elif withdrawal_type == 'BANK' and not bank_details:
            raise forms.ValidationError({
                'bank_details': "Bank details are required for bank withdrawals"
            })

        return cleaned_data 