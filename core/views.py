from django.shortcuts import render, redirect
from .models import Room,Tenant,RoomRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile


def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if hasattr(user, 'profile'):

                if user.profile.role == 'admin':
                    return redirect('admin_dashboard')

                elif user.profile.role == 'owner':
                    return redirect('owner_dashboard')

                else:
                    return redirect('tenant_dashboard')

            else:
                return redirect('tenant_dashboard')

        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')


def room_list(request):
    tenant = Tenant.objects.filter(
            email = request.user.email
    ).first()

    if tenant and tenant.room:
        return redirect('tenant_dashboard')
    
    else:
        rooms = Room.objects.all()

        return render(request, 'room_list.html', {'rooms':rooms})


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
    
def remove_tenant(request, tenant_id):
    tenant = Tenant.objects.get(id = tenant_id)
    tenant.room = None
    tenant.save()
    return redirect('owner_properties')

def tenant_list(request):
    tenants = Tenant.objects.all()
    return render(request, 'tenant_list.html',{'tenants': tenants})

def assign_tenant(request,id):
    room = Room.objects.get(id=id)
    requests = RoomRequest.objects.filter(room=room, status = 'pending')

    tenants = []
    for request_obj in requests:
        tenant_obj = Tenant.objects.filter(
            email = request_obj.tenant.email
        ).first()

        if tenant_obj:
            tenants.append(tenant_obj)

    if request.method == 'POST':
        tenant_id = request.POST.get('tenant')
        tenant = Tenant.objects.get(id = tenant_id)
        tenant.room = room
        tenant.save()

        RoomRequest.objects.filter(
            tenant__email=tenant.email
        ).exclude(
            room=room
        ).update(
            status='rejected'
        )
        return redirect('owner_properties')
    
    else:
        return render(
            request,
            'assign_tenant.html',
            {
                'room': room,
                'tenants': tenants,
                'requests':requests
            }
)
        

@login_required
def request_room(request, room_id):

    room = Room.objects.get(id = room_id)

    if request.method == 'POST':

        message = request.POST.get('message')

        RoomRequest.objects.create(
            tenant = request.user,
            room = room,
            message = message
        )
        return redirect('room_list')

    else:
        return render(request, 'request_room.html',{
            'room':room
        })

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def admin_dashboard(request):
    if request.user.profile.role != 'admin':
        return redirect('tenant_dashboard')

    return render(request, 'admin_dashboard.html')


@login_required
def owner_dashboard(request):
    if request.user.profile.role != 'owner':
        return redirect('tenant_dashboard')

    return render(request, 'owner_dashboard.html')


@login_required
def tenant_dashboard(request):
    if request.user.profile.role != 'tenant':
        return redirect('login')

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
        profile.full_name = request.POST.get('full_name')
        profile.phone_number = request.POST.get('phone_number')
        profile.address = request.POST.get('address')
        profile.save()

        return redirect('profile')

    return render(request, 'edit_profile.html', {
        'profile': profile
    })


def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Email already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.create(
            user=user,
            full_name=full_name,
            role='tenant',
            phone_number=phone_number,
            address=address
        )

        return redirect('login')

    return render(request, 'register.html')
