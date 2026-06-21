from django.contrib import admin
from .models import Room, Tenant, Profile, RoomRequest, ChatMessage

admin.site.register(Room)
admin.site.register(Tenant)
admin.site.register(Profile)
admin.site.register(RoomRequest)
admin.site.register(ChatMessage)