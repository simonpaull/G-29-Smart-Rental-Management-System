# Create your models here.
from django.db import models
from django.contrib.auth.models import User


ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('owner', 'Owner'),
    ('prospect', 'Prospective Tenant'),
    ('tenant', 'Tenant'),
]

TENANT_STATUS_CHOICES = [
    ('new', 'New Tenant'),
    ('verified', 'Verified Tenant'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    phone_number = models.CharField(max_length=20)

    address = models.TextField()

    tenant_status = models.CharField(
        max_length=20,
        choices=TENANT_STATUS_CHOICES,
        blank=True,
        null=True
    )
    
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

#-------------------------------
#Room Table
#-------------------------------
class Room(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = "owned_rooms",
        null = True,
        blank = True
    )

    roomnumber = models.CharField(max_length = 10) 
    roomtype = models.CharField(max_length = 50)
    capacity = models.IntegerField(default=1)
    size = models.CharField(max_length=6)  
    price = models. CharField(max_length = 8)
    availability = models.BooleanField(default = True)  
    description = models.TextField(blank = True, null = True)

    def __str__(self):
        return f"{self.roomnumber} - {self.roomtype}"
    
#-------------------------------
#Tenant Table
#-------------------------------
class Tenant(models.Model):
    name = models.CharField(max_length = 20)

    genderchoices = (
        ('male','Male'),
        ('female','Female')
    )
    gender = models.CharField(max_length = 10, choices= genderchoices, blank=True, null=True)

    contactnumber = models.CharField(max_length = 15)
    email = models.EmailField()
    ic = models.CharField(max_length = 20, blank=True, null=True)
    moveindate = models.DateField(blank=True, null=True)
    moveoutdate = models.DateField(blank = True, null = True)
    room = models.ForeignKey('Room',on_delete = models.SET_NULL, null = True, blank = True)

    def __str__(self):
        if self.room:
            return f"{self.name} ({self.room.roomnumber})"
        else:
            return self.name
        
class RoomRequest(models.Model):

    STATUS_CHOICES = [
        ('pending' , 'Pending'),
        ('accepted' , 'Accepted'),
        ('rejected' , 'Rejected'),
        ('assigned', 'Assigned'),
    ]

    tenant = models.ForeignKey(
        User,
        on_delete = models.CASCADE
    )

    room = models.ForeignKey(
        Room,
        on_delete = models.CASCADE
    )

    message = models.TextField()

    status = models.CharField(
        max_length = 20,
        choices = STATUS_CHOICES,
        default = 'pending'
    )

    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):

        return f"{self.tenant.username} -> {self.room.roomnumber}"


class ChatMessage(models.Model):

    room_request = models.ForeignKey(
        RoomRequest,
        on_delete=models.CASCADE
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.sender.username}"