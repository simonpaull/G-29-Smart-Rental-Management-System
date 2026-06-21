from django.urls import path
from . import views

urlpatterns = [
    path('', views.tenant_payment_dashboard, name='tenant_payment_dashboard'),
    path('<int:payment_id>/', views.payment_page, name='payment_page'),
    path('<int:payment_id>/receipt/', views.download_receipt, name='download_receipt'),
    path('history/', views.payment_history, name='payment_history'),
    path('admin-history/', views.admin_payment_history, name='admin_payment_history'),
    path('admin-summary/', views.admin_summary, name='admin_summary'),
    path('success/', views.payment_success, name='payment_success'),
    path('complaint/', views.complaint_submit, name='complaint_submit'),
    path('complaint/status/', views.complaint_status, name='complaint_status'),
    path('complaint/admin/', views.admin_complaint_status, name='admin_complaint_status'),
    path('complaint/<int:complaint_id>/update/', views.complaint_update, name='complaint_update'),
    path('utility/', views.owner_add_utility, name='owner_add_utility'),
    path('create-payment/', views.admin_create_payment, name='admin_create_payment'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('new-tenant/', views.new_tenant_dashboard, name='new_tenant_dashboard'),
    path('contracts/', views.admin_contracts, name='admin_contracts'),
    path('contracts/create/', views.create_contract, name='create_contract'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/toggle-ban/<int:user_id>/', views.toggle_ban, name='toggle_ban'),
    path('owner-complaint/', views.owner_complaint_submit, name='owner_complaint_submit'),
]