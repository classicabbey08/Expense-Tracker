from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm, SignupForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

def landing(request):
    return render(request, 'landing.html')

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'expense_list.html', {'expenses': expenses})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('expense_list')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})