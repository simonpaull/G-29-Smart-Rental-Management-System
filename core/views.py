from django.shortcuts import render, redirect
<<<<<<< HEAD
from .model import Room,Tenant
=======
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
>>>>>>> 29a69e7d4f3b1f17cf0dd6c79f823ec05cbdf825

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

<<<<<<< HEAD
def dashboard(request):
    return render(request, 'dashboard.html')


def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'room_list.html', {'rooms': rooms})

def owner_properties(request):
    rooms = Room.objects.all()
    return render(request, 'owner_properties.html', {'rooms': rooms})


def add_room(request):
    if request.method == 'POST':
        roomnumber = request.POST.get('roomnumber')
        roomtype = request.POST.get('roomtype')
        capacity = request.POST.get('capacity')
        size = request.POST.get('size')
        price = request.POST.get('price')

            
        description = request.POST.get('description')


        Room.objects.create(
            roomnumber = roomnumber,  #fieldname(from model.py) = variable 
            roomtype = roomtype,
            capacity = capacity,
            size = size,
            price = price,
            description = description
        )

        return redirect('owner_properties')
    
    else:
         return render(request, 'add_room.html')
        
def edit_room(request, id):
    room = Room.objects.get(id=id)

    if request.method =="POST" :
        room.roomnumber = request.POST.get('roomnumber')
        room.roomtype = request.POST.get('roomtype')
        room.capacity = request.POST.get('capacity')
        room.size = request.POST.get('size')
        room.price = request.POST.get('price')
        
        
        room.description = request.POST.get('description')
        room.save()
        return redirect('owner_properties')
    
    else:
        return render(request, 'edit_room.html', {'room': room})
    
def delete_room(request, id):
    room = Room.objects.get(id=id)

    if request.method == 'POST':
        room.delete()
        return redirect('owner_properties')
    else:
        return render(request,'delete_room.html',{'room':room})

def tenant_list(request):
    tenants = Tenant.objects.all()
    return render(request, 'tenant_list.html',{'tenants': tenants})

def assign_tenant(request,id):
    room = Room.objects.get(id=id)
    tenants = Tenant.objects.all()

    if request.method == 'POST':
        tenant_id = request.POST.get('tenant')
        tenant = Tenant.objects.get(id = tenant_id)
        tenant.room = room
        tenant.save()
        return redirect('owner_properties')
    
    else:
        return render(
            request,
            'assign_tenant.html',
            {
                'room': room,
                'tenants': tenants
            }
)
        
=======
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

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.create(
            user=user,
            role=role,
            phone_number=phone_number,
            address=address
        )

        return redirect('login')

    return render(request, 'register.html')
>>>>>>> 29a69e7d4f3b1f17cf0dd6c79f823ec05cbdf825
