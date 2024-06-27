from django import forms
from apps.api.specialists.models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ['phone_number']

