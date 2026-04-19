from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('tenant', 'Tenant'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tenant')
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username