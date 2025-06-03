from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if email or password is missing
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return redirect('login')

        # Check if the email exists in the system
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'No account found with this email.')
            return redirect('login')

        # Try to authenticate the user
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.name}!')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
            return redirect('login')

    return render(request, 'pages/signin.html')

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')  # NEW: get mobile input

        # Basic validation: All fields must be filled
        if not name or not email or not password or not mobile:
            messages.error(request, 'Please fill out all fields.')
            return redirect('signup')

        # Email format validation (basic check)
        if '@' not in email or '.' not in email:
            messages.error(request, 'Please enter a valid email address.')
            return redirect('signup')

        # Password strength (basic check)
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return redirect('signup')

        # Mobile number basic length check
        if len(mobile) < 10:
            messages.error(request, 'Please enter a valid mobile number.')
            return redirect('signup')

        # Check if user with this email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered. Please use a different email or log in.')
            return redirect('signup')

        # All good, create and login user
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            name=name,
            mobile=mobile  # NEW: save mobile
        )
        login(request, user)
        messages.success(request, f'Welcome, {name}!')
        return redirect('home')

    return render(request, 'pages/signin.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')