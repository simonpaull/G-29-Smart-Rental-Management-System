from django.contrib import admin
from .models import Room, Tenant, Profile

admin.site.register(Room)
admin.site.register(Tenant)
admin.site.register(Profile)