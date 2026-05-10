from django.shortcuts import render, redirect
from .model import Room,Tenant

def home(request):
    return render(request, 'home.html')

def login_view(request):
    return render(request, 'login.html')

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

        if request.POST.get('availability') :
            availability = True
        else:
            availability = False
            
        description = request.POST.get('description')


        Room.objects.create(
            roomnumber = roomnumber,  #fieldname(from model.py) = variable 
            roomtype = roomtype,
            capacity = capacity,
            size = size,
            price = price,
            availability = availability,
            description = description
        )

        return redirect('room_list')
    
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
            
        if request.POST.get('availability'):
            room.availability = True
        else:
            room.availability = False
        
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
        
