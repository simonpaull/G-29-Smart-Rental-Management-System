from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Payment

def payment_page(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        payment.status = 'paid'
        payment.paid_date = timezone.now().date()
        payment.save()
        return redirect('payment_success')

    return render(request, 'payment/payment.html', {
        'payment': payment
    })

def payment_history(request):
    payments = Payment.objects.all().order_by('-due_date')
    return render(request, 'payment/history.html', {
        'payments': payments
    })

def payment_success(request):
    return render(request, 'payment/success.html')