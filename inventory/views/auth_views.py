# inventory/views/auth_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group

from ..forms import UserRegistrationForm
from ..models import Employee

def login_view(request):
    """
    Handles user login. If the user is already authenticated,
    they are redirected to the main dashboard.
    """
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')

    if request.method == 'POST':
        username_from_form = request.POST.get('username')
        password_from_form = request.POST.get('password')
        
        user = authenticate(request, username=username_from_form, password=password_from_form)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('inventory:dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            
    return render(request, 'inventory/auth/login.html')

def logout_view(request):
    """Logs the current user out and redirects to the login page."""
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('inventory:login')

def register_view(request):
    """Handles new user registration for 'Employee' and 'IT_Admin' roles."""
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            Employee.objects.create(
                user=new_user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email']
            )

            selected_role = form.cleaned_data['role']
            try:
                group = Group.objects.get(name=selected_role)
                new_user.groups.add(group)
            except Group.DoesNotExist:
                messages.error(request, 'A server error occurred: The selected role does not exist.')
                new_user.delete() # Clean up the created user
                return render(request, 'inventory/auth/register.html', {'form': form})

            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('inventory:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'inventory/auth/register.html', {'form': form})

def access_denied_view(request):
    """Displays the 'Access Denied' page."""
    return render(request, 'inventory/auth/access_denied.html')