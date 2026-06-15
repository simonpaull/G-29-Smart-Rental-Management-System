from django.db import models
from django.contrib.auth.models import User


ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('owner', 'Owner'),
    ('prospect', 'Prospective Tenant'),
    ('tenant', 'Tenant'),
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

    
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"