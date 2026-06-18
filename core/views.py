from django.shortcuts import render, redirect
from .models import Room,Tenant,RoomRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
import random
from django.core.mail import send_mail
from django.conf import settings


def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

<<<<<<< HEAD
            if user.profile.role == 'admin':
                return redirect('owner_dashboard')
            else:
                return redirect('tenant_payment_dashboard')  # ← point to your dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
=======
            if hasattr(user, 'profile'):
                if user.profile.role == 'admin':
                    return redirect('admin_dashboard')

                elif user.profile.role == 'owner':
                    return redirect('owner_dashboard')
                
                elif user.profile.role == 'prospect':
                    return redirect('prospect_dashboard')

                elif user.profile.role == 'tenant':
                    return redirect('tenant_dashboard')

            return redirect('login')

        return render(request, 'login.html', {
            'error': 'Invalid username or password'
        })
>>>>>>> dfe1b60b9d0662f25beaf51e5e55c8992d42db90

    return render(request, 'login.html')

@login_required
def dashboard(request):

    role = request.user.profile.role

    if role == 'admin':
        return redirect('admin_dashboard')

    elif role == 'owner':
        return redirect('owner_dashboard')

    elif role == 'prospect':
        return redirect('prospect_dashboard')

    elif role == 'tenant':
        return redirect('tenant_dashboard')

    return redirect('login')


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

@login_required
def assign_tenant(request, id):

    room = Room.objects.get(id=id)

    requests = RoomRequest.objects.filter(
        room=room
    )

    accepted_requests = RoomRequest.objects.filter(
        room=room,
        status='accepted'
    )

    if request.method == 'POST':

        request_id = request.POST.get('tenant')

        room_request = RoomRequest.objects.get(
            id=request_id
        )

        user = room_request.tenant

        tenant, created = Tenant.objects.get_or_create(
            email=user.email,
            defaults={
                'name': user.username,
                'contactnumber': '',
                'room': room
            }
        )

        tenant.room = room
        tenant.save()

        user.profile.role = 'tenant'
        user.profile.save()

        room_request.status= 'assigned'
        room_request.save()

        RoomRequest.objects.filter(
            tenant=user
        ).exclude(
            room=room
        ).update(
            status='rejected'
        )

        return redirect('owner_properties')

    return render(
        request,
        'assign_tenant.html',
        {
            'room': room,
            'accepted_requests': accepted_requests,
            'requests': requests
        }
    )
        
@login_required
def request_room(request, room_id):

    room = Room.objects.get(id=room_id)

    existing_request = RoomRequest.objects.filter(
        tenant=request.user,
        status='pending'
    ).exists()

    if existing_request:
        return render(
            request,
            'request_room.html',
            {
                'room': room,
                'error': 'You already have an active room request. Please wait for the owner response.'
            }
        )

    if request.method == 'POST':

        message = request.POST.get('message')

        RoomRequest.objects.create(
            tenant=request.user,
            room=room,
            message=message
        )

        return redirect('room_list')

    return render(
        request,
        'request_room.html',
        {
            'room': room
        }
    )


@login_required
def my_applications(request):

    requests = RoomRequest.objects.filter(
        tenant=request.user
    )

    return render(
        request,
        'my_applications.html',
        {
            'requests': requests
        }
    )


@login_required
def my_room(request):

    tenant = Tenant.objects.filter(
        email=request.user.email
    ).last()

    roommates = []

    if tenant and tenant.room:

        roommates = Tenant.objects.filter(
            room=tenant.room
        ).exclude(
            id=tenant.id
        )

    return render(
        request,
        'my_room.html',
        {
            'tenant': tenant,
            'roommates': roommates
        }
    )

def update_request_status(request,request_id,status):
    room_request  = RoomRequest.objects.get(id = request_id)

    if status == 'rejected':
        room_request.delete()

    else:
        room_request.status = status
        room_request.save()

    return redirect( 'assign_tenant', room_request.room.id )

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

    new_requests = RoomRequest.objects.filter(
        room__owner=request.user,
        status='pending'
    )

    return render(
        request,
        'owner_dashboard.html',
        {
            'new_requests': new_requests
        }
    )


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

@login_required
def prospect_dashboard(request):
    return render(request, 'prospect_dashboard.html')

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

        otp = str(random.randint(100000, 999999))

        request.session['otp'] = otp

        request.session['registration_data'] = {
            'full_name': full_name,
            'username': username,
            'email': email,
            'password': password,
            'phone_number': phone_number,
            'address': address,
        }

        send_mail(
            'Email Verification',
            f'Your verification code is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return redirect('verify_email')

    return render(request, 'register.html')

def verify_email(request):

    if request.method == 'POST':

        entered_otp = request.POST.get('otp')

        stored_otp = request.session.get('otp')

        if entered_otp == stored_otp:

            data = request.session.get('registration_data')

            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )

            Profile.objects.create(
                user=user,
                full_name=data['full_name'],
                role='prospect',
                phone_number=data['phone_number'],
                address=data['address'],
                email_verified=True
            )

            del request.session['otp']
            del request.session['registration_data']

            return redirect('login')

        return render(
            request,
            'verify_email.html',
            {
                'error': 'Invalid verification code'
            }
        )

    return render(
        request,
        'verify_email.html'
    )


@login_required
def cancel_application(request, request_id):

    room_request = RoomRequest.objects.get(id=request_id)

    if room_request.tenant == request.user:
        room_request.delete()

    return redirect('my_applications')