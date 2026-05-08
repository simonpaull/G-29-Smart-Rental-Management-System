from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('login/', views.login_view),
    path('dashboard/', views.dashboard),

    path('rooms/', views.room_list, name ='room_list'),
    path('tenant-list/', views.tenant_list, name='tenant_list'),
    path('owner-properties/', views.owner_properties, name='owner_properties'),
    
    path('add-room/', views.add_room, name = 'add_room'),
    path('edit-room/<int:id>/', views.edit_room, name = 'edit_room' ),
    path('delete-room/<int:id>/', views.delete_room, name='delete_room'),

]
