from django.urls import path
from . import views

urlpatterns = [
    path('', views.tenant_payment_dashboard, name='tenant_payment_dashboard'),
    path('<int:payment_id>/', views.payment_page, name='payment_page'),
    path('history/', views.payment_history, name='payment_history'),
    path('admin-history/', views.admin_payment_history, name='admin_payment_history'),
    path('success/', views.payment_success, name='payment_success'),
]