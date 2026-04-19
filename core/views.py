from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if hasattr(user, 'profile') and user.profile.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('tenant_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_dashboard(request):
    if request.user.profile.role != 'admin':
        return redirect('tenant_dashboard')
    return render(request, 'admin_dashboard.html')

@login_required
def tenant_dashboard(request):
    return render(request, 'tenant_dashboard.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html', {
        'profile': request.user.profile
    })

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.phone_number = request.POST.get('phone_number')
        profile.address = request.POST.get('address')
        profile.save()
        return redirect('profile')

    return render(request, 'edit_profile.html', {'profile': profile})