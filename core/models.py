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