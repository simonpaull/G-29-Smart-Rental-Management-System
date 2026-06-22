from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home),
    path('login/', views.login_view),
    path('dashboard/', views.dashboard),

    path('rooms/', views.room_list, name ='room_list'),
    path('tenant-list/', views.tenant_list, name='tenant_list'),
    path('owner-properties/', views.owner_properties, name='owner_properties'),
    path('request-room/<int:room_id>/', views.request_room, name='request_room'),
    path('add-room/', views.add_room, name = 'add_room'),
    path('edit-room/<int:id>/', views.edit_room, name = 'edit_room' ),
    path('delete-room/<int:id>/', views.delete_room, name='delete_room'),
    path('assign-tenant/<int:id>/',views.assign_tenant,name='assign_tenant'),
    path('remove-tenant/<int:tenant_id>/', views.remove_tenant, name = 'remove_tenant'),
    path('request-status/<int:request_id>/<str:status>/', views.update_request_status, name='update_request_status'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-room/', views.my_room, name='my_room'),
    path('cancel-application/<int:request_id>/', views.cancel_application, name='cancel_application'),
    path('chat/<int:request_id>/', views.chat_room, name='chat_room'),
    
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path(
        'create-owner/',
         views.create_owner,
            name='create_owner'
 ),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path(
        'create-tenant/',
         views.create_tenant,
            name='create_tenant'
    ),
    path('tenant-dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='change_password.html',
            success_url='/change-password-done/'
        ),
        name='change_password'
    ),
    path(
        'change-password-done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='change_password_done.html'
        ),
        name='password_change_done'
    ),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html'
        ),
        name='password_reset'
    ),
    path(
        'password-reset-done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset-done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path(
        'prospect-dashboard/',
         views.prospect_dashboard,
        name='prospect_dashboard'
    ),
    path(
        'verify-email/',
         views.verify_email,
        name='verify_email'
    ),
]