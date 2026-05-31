from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment

def check_overdue_payments():
    today = timezone.now().date()
    
    # Find unpaid payments where due date has passed
    overdue_payments = Payment.objects.filter(
        status='unpaid',
        due_date__lt=today
    )
    
    for payment in overdue_payments:
        # Change status to overdue
        payment.status = 'overdue'
        payment.save()

        # Send email only once when first becoming overdue
        send_mail(
            subject=f'⚠️ Overdue Payment Reminder - {payment.period()}',
            message=f'Dear {payment.tenant.get_full_name() or payment.tenant.username},\n\nYour payment of RM {payment.total()} for {payment.period()} is OVERDUE.\n\nDue date was: {payment.due_date}\n\nPlease make payment as soon as possible.\n\nThank you!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.tenant.email],
            fail_silently=True,
        )
    
    return overdue_payments.count()