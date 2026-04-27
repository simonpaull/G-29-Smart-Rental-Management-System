from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Payment

@login_required
def payment_page(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, tenant=request.user)

    if request.method == 'POST':
        payment.status = 'paid'
        payment.paid_date = timezone.now().date()
        payment.save()
        return redirect('payment_success')

    return render(request, 'payment/payment.html', {
        'payment': payment
    })

@login_required
def payment_history(request):
    payments = Payment.objects.filter(tenant=request.user).order_by('-due_date')
    return render(request, 'payment/history.html', {
        'payments': payments
    })

@login_required
def admin_payment_history(request):
    if request.user.profile.role != 'admin':
        return redirect('payment_history')
    payments = Payment.objects.all().order_by('-due_date')
    return render(request, 'payment/admin_history.html', {
        'payments': payments
    })

def payment_success(request):
    return render(request, 'payment/success.html')