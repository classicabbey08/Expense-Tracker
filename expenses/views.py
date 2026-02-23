from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views import View
from .forms import CustomUserCreationForm  # ← we'll create this next

# Option 1: Function-based view (simple & good for now)
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optional: auto-login after signup
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}.")
            return redirect('dashboard')  # or 'child_dashboard' / 'parent_dashboard' later
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})


# Option 2: Class-based view (cleaner, more reusable - recommended long-term)
class SignUpView(View):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors in the form.")
        return render(request, self.template_name, {'form': form})


# Landing view - unchanged, but good practice to add context if needed
def landing(request):
    return render(request, 'landing.html', {
        'title': 'Expense Vault - Family Pocket Money Tracker'
    })