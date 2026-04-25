from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('login/', views.login_view),
    path('dashboard/', views.dashboard),

    path('rooms/', views.room_list, name ='room_list'),
    path('add-room/', views.add_room, name = 'add_room'),
   
]
