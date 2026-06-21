from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment
from django.contrib.auth.models import User

def check_overdue_payments():
    today = timezone.now().date()
    
    # Find all unpaid payments where due date has passed
    overdue_payments = Payment.objects.filter(
        status='unpaid',
        due_date__lt=today
    )
    
    # Group by tenant
    tenant_overdue = {}
    for payment in overdue_payments:
        tenant_id = payment.tenant.id
        if tenant_id not in tenant_overdue:
            tenant_overdue[tenant_id] = {
                'tenant': payment.tenant,
                'payments': []
            }
        tenant_overdue[tenant_id]['payments'].append(payment)
    
    # Send ONE combined email per tenant
    for tenant_id, data in tenant_overdue.items():
        tenant = data['tenant']
        payments = data['payments']
        
        # Build combined payment details
        payment_details = ''
        total_overdue = 0
        for p in payments:
            p.status = 'overdue'
            p.save()
            payment_details += f'\n- {p.period()} | Unit {p.unit} | RM {p.total()} | Due: {p.due_date}'
            total_overdue += p.total()
        
        # Send one combined email
        if tenant.email:
            send_mail(
                subject=f'⚠️ Overdue Payment Reminder — {len(payments)} payment(s) overdue',
                message=f'Dear {tenant.get_full_name() or tenant.username},\n\nYou have {len(payments)} overdue payment(s):\n{payment_details}\n\nTotal overdue amount: RM {total_overdue}\n\nPlease make payment as soon as possible.\n\nThank you!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[tenant.email],
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

def auto_detect_priority(title, description):
    text = (title + ' ' + description).lower()

    high_keywords = [
        'fire', 'flood', 'electric shock', 'gas leak', 'no water',
        'water cut', 'power outage', 'no electricity', 'burst pipe',
        'broken door', 'broken lock', 'security', 'emergency',
        'dangerous', 'urgent', 'immediately', 'serious', 'injury',
        'accident', 'collapsed', 'ceiling fell', 'cannot enter',
        'sewage', 'overflow', 'rodent', 'pest', 'rats', 'cockroach',
        'nothing coming out', 'no water coming', 'cannot bath',
        'cant bath', 'cannot shower', 'cant shower', 'no supply',
        'electric trip', 'short circuit', 'tiada air', 'tiada elektrik',
        'paip pecah', 'bahaya', 'kecemasan', 'banjir', 'kebakaran'
    ]

    medium_keywords = [
        'leaking', 'leak', 'water leak', 'dripping', 'not working',
        'broken', 'damaged', 'spoiled', 'repair', 'fix',
        'air cond', 'aircon', 'air conditioning', 'heater',
        'hot water', 'wifi', 'internet', 'elevator', 'lift',
        'washing machine', 'refrigerator', 'fridge', 'stove',
        'toilet', 'flush', 'sink', 'drain', 'blocked', 'clogged',
        'noise', 'neighbour', 'neighbor', 'smell', 'mould', 'mold',
        'rosak', 'bocor', 'tak boleh', 'tidak boleh', 'slow', 'dirty'
    ]

    for keyword in high_keywords:
        if keyword in text:
            return 'high'

    for keyword in medium_keywords:
        if keyword in text:
            return 'medium'

    return 'low'