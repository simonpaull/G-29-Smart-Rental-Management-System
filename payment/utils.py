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

def auto_detect_priority(title, description):
    text = (title + ' ' + description).lower()

    high_keywords = [
        'fire', 'flood', 'electric shock', 'gas leak', 'no water',
        'water cut', 'power outage', 'no electricity', 'burst pipe',
        'broken door', 'broken lock', 'security', 'emergency',
        'dangerous', 'urgent', 'immediately', 'serious', 'injury',
        'accident', 'collapsed', 'ceiling fell', 'cannot enter',
        'sewage', 'overflow', 'rodent', 'pest', 'rats', 'cockroach'
    ]

    medium_keywords = [
        'leaking', 'leak', 'water leak', 'dripping', 'not working',
        'broken', 'damaged', 'spoiled', 'repair', 'fix',
        'air cond', 'aircon', 'air conditioning', 'heater',
        'hot water', 'wifi', 'internet', 'elevator', 'lift',
        'washing machine', 'refrigerator', 'fridge', 'stove',
        'toilet', 'flush', 'sink', 'drain', 'blocked', 'clogged',
        'noise', 'neighbour', 'neighbor', 'smell', 'mould', 'mold'
    ]

    # Check high priority first
    for keyword in high_keywords:
        if keyword in text:
            return 'high'

    # Check medium priority
    for keyword in medium_keywords:
        if keyword in text:
            return 'medium'

    # Default to low
    return 'low'