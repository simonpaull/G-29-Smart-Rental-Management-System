from django.urls import path
from . import views

urlpatterns = [
    path('', views.tenant_payment_dashboard, name='tenant_payment_dashboard'),
    path('<int:payment_id>/', views.payment_page, name='payment_page'),
    path('<int:payment_id>/receipt/', views.download_receipt, name='download_receipt'),
    path('history/', views.payment_history, name='payment_history'),
    path('admin-history/', views.admin_payment_history, name='admin_payment_history'),
    path('success/', views.payment_success, name='payment_success'),

    # Complaint URLs
    path('complaint/', views.complaint_submit, name='complaint_submit'),
    path('complaint/status/', views.complaint_status, name='complaint_status'),
    path('complaint/admin/', views.admin_complaint_status, name='admin_complaint_status'),
    path('complaint/<int:complaint_id>/update/', views.complaint_update, name='complaint_update'),
]