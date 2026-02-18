from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category', 'description']
        labels = {
            'title': 'Child / Category',
            'amount': 'Amount (₦)',
            'date': 'Date',
            'category': 'Frequency (Weekly / Monthly / Yearly)',
            'description': 'Notes (optional)',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        labels = {
            'username': 'Parent Username',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
