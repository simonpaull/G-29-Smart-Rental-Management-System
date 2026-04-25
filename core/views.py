from django.shortcuts import render, redirect
from .model import Room

def home(request):
    return render(request, 'home.html')

def login_view(request):
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')


def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'room_list.html', {'rooms': rooms})


def add_room(request):
    if request.method == 'POST':
        roomnumber = request.POST.get('roomnumber')
        roomtype = request.POST.get('roomtype')
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
            size = size,
            price = price,
            availability = availability,
            description = description
        )

        return redirect('room_list')
    
    else:
         return render(request, 'add_room.html')
        
    