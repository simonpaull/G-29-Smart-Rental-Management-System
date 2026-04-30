from django.db import models

#-------------------------------
#Room Table
#-------------------------------
class Room(models.Model):
    roomnumber = models.CharField(max_length = 10) 
    roomtype = models.CharField(max_length = 50)
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
    gender = models.CharField(max_length = 10, choices= genderchoices)

    contactnumber = models.CharField(max_length = 15)
    email = models.EmailField()
    ic = models.CharField(max_length = 20)
    moveindate = models.DateField()
    moveoutdate = models.DateField(blank = True, null = True)
    room = models.ForeignKey('Room',on_delete = models.SET_NULL, null = True, blank = True)

    def __str__(self):
        if self.room:
            return f"{self.name} ({self.room.roomnumber})"
        else:
            return self.name