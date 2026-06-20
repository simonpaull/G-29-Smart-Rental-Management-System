from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Payment, Complaint
from .utils import check_overdue_payments, auto_detect_priority
from .models import Payment, Complaint, RentalContract

import io

def generate_receipt_pdf(payment):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Smart Rental Management System", styles['Title']))
    elements.append(Paragraph("Payment Receipt", styles['Heading2']))
    elements.append(Spacer(1, 20))

    data = [
        ['Receipt Details', ''],
        ['Tenant', payment.tenant.get_full_name() or payment.tenant.username],
        ['Unit', payment.unit],
        ['Period', payment.period()],
        ['Rent', f'RM {payment.rent}'],
        ['Electric', f'RM {payment.electric}'],
        ['Water', f'RM {payment.water}'],
        ['Total Utility', f'RM {payment.utility()}'],
        ['Total Amount', f'RM {payment.total()}'],
        ['Payment Date', str(payment.paid_date)],
        ['Status', payment.status.upper()],
    ]

    table = Table(data, colWidths=[200, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#534AB7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F5F5F5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for your payment!", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

@login_required(login_url='/login/')
def payment_page(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, tenant=request.user)

    if request.method == 'POST':
        payment.status = 'paid'
        payment.paid_date = timezone.now().date()
        payment.save()

        # Generate PDF
        pdf_buffer = generate_receipt_pdf(payment)

        # Send email with PDF attachment
        email = EmailMessage(
            subject=f'Payment Receipt - {payment.period()}',
            body=f'Dear {payment.tenant.get_full_name() or payment.tenant.username},\n\nYour payment of RM {payment.total()} for {payment.period()} has been received.\n\nPlease find your receipt attached.\n\nThank you!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[payment.tenant.email],
        )
        email.attach(
            filename=f'receipt_{payment.id}_{payment.period()}.pdf',
            content=pdf_buffer.getvalue(),
            mimetype='application/pdf'
        )
        email.send(fail_silently=True)

        return redirect('payment_success')

    return render(request, 'payment/payment.html', {
        'payment': payment
    })

@login_required(login_url='/login/')
def payment_history(request):
    payments = Payment.objects.filter(tenant=request.user).order_by('-due_date')
    return render(request, 'payment/history.html', {
        'payments': payments
    })

@login_required(login_url='/login/')
def admin_payment_history(request):
    if request.user.profile.role not in ['admin', 'owner']:
        return redirect('tenant_payment_dashboard')
    
    check_overdue_payments()
    
    payments = Payment.objects.all().order_by('-due_date')
    return render(request, 'payment/admin_history.html', {
        'payments': payments
    })

def payment_success(request):
    return render(request, 'payment/success.html')

@login_required(login_url='/login/')
def tenant_payment_dashboard(request):
    check_overdue_payments()

    unpaid = Payment.objects.filter(
        tenant=request.user,
        status='unpaid'
    ).order_by('due_date')

    overdue_raw = Payment.objects.filter(
        tenant=request.user,
        status='overdue'
    ).order_by('due_date')

    # Group overdue payments by unit
    overdue_grouped = {}
    for p in overdue_raw:
        if p.unit not in overdue_grouped:
            overdue_grouped[p.unit] = {
                'unit': p.unit,
                'payments': [],
                'total': 0,
                'earliest_due': p.due_date,
                'periods': [],
            }
        overdue_grouped[p.unit]['payments'].append(p)
        overdue_grouped[p.unit]['total'] += p.total()
        overdue_grouped[p.unit]['periods'].append(p.period())
        if p.due_date < overdue_grouped[p.unit]['earliest_due']:
            overdue_grouped[p.unit]['earliest_due'] = p.due_date

    overdue = list(overdue_grouped.values())

    history = Payment.objects.filter(
        tenant=request.user
    ).order_by('-due_date')

    return render(request, 'payment/tenant_dashboard.html', {
        'unpaid': unpaid,
        'overdue': overdue,
        'history': history
    })

@login_required(login_url='/login/')
def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if payment.tenant != request.user and request.user.profile.role != 'admin':
        return redirect('payment_history')

    pdf_buffer = generate_receipt_pdf(payment)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}_{payment.period()}.pdf"'
    return response

from .models import Payment, Complaint

@login_required(login_url='/login/')
def complaint_submit(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        # Auto detect priority based on keywords
        priority = auto_detect_priority(title, description)

        complaint = Complaint.objects.create(
            tenant=request.user,
            title=title,
            description=description,
            priority=priority,
        )

        # Send email to all admins
        from django.contrib.auth.models import User
        admins = User.objects.filter(profile__role='admin')
        admin_emails = [admin.email for admin in admins if admin.email]

        if admin_emails:
            send_mail(
                subject=f'New Complaint Received - {priority.upper()} Priority',
                message=f'A new complaint has been submitted.\n\nTenant: {request.user.get_full_name() or request.user.username}\nTitle: {title}\nPriority: {priority.upper()}\nDescription: {description}\n\nPlease login to review.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=True,
            )

        return redirect('complaint_status')

    return render(request, 'payment/complaint_submit.html')

# Tenant — view own complaints
@login_required(login_url='/login/')
def complaint_status(request):
    complaints = Complaint.objects.filter(tenant=request.user)
    return render(request, 'payment/complaint_status_tenant.html', {
        'complaints': complaints
    })

# Admin — view all complaints sorted by priority
@login_required(login_url='/login/')
def admin_complaint_status(request):
    if request.user.profile.role != 'admin':
        return redirect('complaint_status')
    complaints = Complaint.objects.all()
    return render(request, 'payment/complaint_status_admin.html', {
        'complaints': complaints
    })

# Admin — update complaint status
@login_required(login_url='/login/')
def complaint_update(request, complaint_id):
    if request.user.profile.role != 'admin':
        return redirect('complaint_status')

    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        complaint.status = request.POST.get('status')
        complaint.admin_notes = request.POST.get('admin_notes')
        complaint.save()
        return redirect('admin_complaint_status')

    return render(request, 'payment/complaint_update.html', {
        'complaint': complaint
    })

# Admin — payment summary dashboard
@login_required(login_url='/login/')
def admin_summary(request):
    if request.user.profile.role != 'admin':
        return redirect('tenant_payment_dashboard')

    check_overdue_payments()

    from django.db.models import Sum

    total_collected = Payment.objects.filter(status='paid').aggregate(Sum('rent'))['rent__sum'] or 0
    total_utility_collected = sum(p.utility() for p in Payment.objects.filter(status='paid'))
    total_paid = Payment.objects.filter(status='paid').count()
    total_unpaid = Payment.objects.filter(status='unpaid').count()
    total_overdue = Payment.objects.filter(status='overdue').count()
    total_complaints_pending = Complaint.objects.filter(status='pending').count()
    total_complaints_inprogress = Complaint.objects.filter(status='in_progress').count()
    total_complaints_resolved = Complaint.objects.filter(status='resolved').count()
    recent_payments = Payment.objects.filter(status='paid').order_by('-paid_date')[:5]

    return render(request, 'payment/admin_summary.html', {
        'total_collected': total_collected,
        'total_utility_collected': total_utility_collected,
        'total_paid': total_paid,
        'total_unpaid': total_unpaid,
        'total_overdue': total_overdue,
        'total_complaints_pending': total_complaints_pending,
        'total_complaints_inprogress': total_complaints_inprogress,
        'total_complaints_resolved': total_complaints_resolved,
        'recent_payments': recent_payments,
    })

@login_required(login_url='/login/')
def owner_add_utility(request):
    if request.user.profile.role != 'admin':
        return redirect('tenant_payment_dashboard')

    # Get all unpaid payments
    payments = Payment.objects.filter(status='unpaid').order_by('due_date')

    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        electric = request.POST.get('electric')
        water = request.POST.get('water')

        payment = get_object_or_404(Payment, id=payment_id)
        payment.electric = electric
        payment.water = water
        payment.save()

        return redirect('owner_add_utility')

    return render(request, 'payment/owner_add_utility.html', {
        'payments': payments
    })

@login_required(login_url='/login/')
def admin_create_payment(request):
    if request.user.profile.role != 'admin':
        return redirect('tenant_payment_dashboard')

    from core.models import Room, Tenant
    from django.contrib.auth.models import User

    # Get all tenants with rooms
    tenants = Tenant.objects.filter(room__isnull=False)

    if request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        period_month = request.POST.get('period_month')
        period_year = request.POST.get('period_year')
        electric = request.POST.get('electric', 0)
        water = request.POST.get('water', 0)
        due_date = request.POST.get('due_date')

        # Get tenant details
        tenant_obj = Tenant.objects.get(id=tenant_id)
        room = tenant_obj.room

        # Auto read rent from room
        rent = room.price
        unit = room.roomnumber

        # Get the Django User linked to this tenant
        # Match by email
        try:
            user = User.objects.get(email=tenant_obj.email)
        except User.DoesNotExist:
            user = None

        if user:
            Payment.objects.create(
                tenant=user,
                unit=unit,
                period_month=period_month,
                period_year=period_year,
                rent=rent,
                electric=electric,
                water=water,
                status='unpaid',
                due_date=due_date,
            )

            # Send email to tenant
            send_mail(
                subject=f'New Payment Due - {period_month} {period_year}',
                message=f'Dear {tenant_obj.name},\n\nA new payment has been created.\n\nUnit: {unit}\nPeriod: {period_month} {period_year}\nRent: RM {rent}\nDue date: {due_date}\n\nPlease login to make payment.\n\nThank you!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[tenant_obj.email],
                fail_silently=True,
            )

        return redirect('admin_payment_history')

    return render(request, 'payment/admin_create_payment.html', {
        'tenants': tenants,
        'month_choices': [
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ],
        'year_choices': ['2025', '2026', '2027'],
    })

@login_required(login_url='/login/')
def owner_dashboard(request):
    if request.user.profile.role != 'admin':
        return redirect('tenant_payment_dashboard')

    check_overdue_payments()

    # Payment stats
    total_collected = sum(p.total() for p in Payment.objects.filter(status='paid'))
    total_overdue = Payment.objects.filter(status='overdue').count()
    total_complaints = Complaint.objects.filter(status='pending').count()
    pending_complaints = Complaint.objects.filter(status='pending').order_by('priority')
    recent_payments = Payment.objects.all().order_by('-due_date')[:5]

    # Try to get room data from Simon's models
    rooms = []
    room_requests = []
    try:
        from core.models import Room, RoomRequest
        rooms = Room.objects.filter(owner=request.user)
        room_requests = RoomRequest.objects.filter(
            room__owner=request.user,
            status='pending'
        ).order_by('-created_at')
    except Exception:
        pass

    return render(request, 'payment/owner_dashboard.html', {
        'total_collected': total_collected,
        'total_overdue': total_overdue,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'rooms': rooms,
        'room_requests': room_requests,
        'recent_payments': recent_payments,
    })

@login_required(login_url='/login/')
def new_tenant_dashboard(request):
    available_rooms = []
    my_requests = []
    
    try:
        from core.models import Room, RoomRequest
        available_rooms = Room.objects.filter(availability=True)
        my_requests = RoomRequest.objects.filter(
            tenant=request.user
        ).order_by('-created_at')
    except Exception:
        pass

    return render(request, 'payment/new_tenant_dashboard.html', {
        'available_rooms': available_rooms,
        'my_requests': my_requests,
    })

@login_required(login_url='/login/')
def create_contract(request):
    if request.user.profile.role != 'admin':
        return redirect('tenant_payment_dashboard')

    from django.contrib.auth.models import User
    tenants_with_users = []

    try:
        from core.models import Tenant
        tenant_records = Tenant.objects.filter(room__isnull=False)
        for t in tenant_records:
            try:
                user = User.objects.get(email=t.email)
                tenants_with_users.append({
                    'user': user,
                    'tenant_record': t,
                    'room': t.room,
                })
            except User.DoesNotExist:
                continue
    except Exception:
        pass

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        unit = request.POST.get('unit')
        start_date = request.POST.get('start_date')
        duration = request.POST.get('duration_months')
        rent = request.POST.get('monthly_rent')
        electric = request.POST.get('electric_rate')
        water = request.POST.get('water_rate')

        tenant_user = User.objects.get(id=user_id)

        contract = RentalContract.objects.create(
            tenant=tenant_user,
            unit=unit,
            start_date=start_date,
            duration_months=int(duration),
            monthly_rent=rent,
            electric_rate=electric or 0,
            water_rate=water or 0,
        )
        contract.generate_payments()

        send_mail(
            subject='Rental Contract Created',
            message=f'Dear {tenant_user.get_full_name() or tenant_user.username},\n\nYour rental contract has been created.\n\nUnit: {unit}\nStart date: {start_date}\nDuration: {duration} months\nMonthly rent: RM {rent}\n\nYour monthly payments have been set up automatically.\n\nThank you!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[tenant_user.email],
            fail_silently=True,
        )

        return redirect('admin_contracts')

    return render(request, 'payment/create_contract.html', {
        'tenants_with_users': tenants_with_users
    })

@login_required(login_url='/login/')
def admin_contracts(request):
    if request.user.profile.role != 'admin':
        return redirect('tenant_payment_dashboard')
    contracts = RentalContract.objects.all().order_by('-created_at')
    return render(request, 'payment/admin_contracts.html', {
        'contracts': contracts
    })

@login_required(login_url='/login/')
def admin_panel(request):
    if request.user.profile.role != 'admin':
        return redirect('owner_dashboard')

    from django.contrib.auth.models import User

    users = User.objects.all().select_related('profile').order_by('-date_joined')
    total_users = users.count()
    total_owners = users.filter(profile__role='owner').count() + users.filter(profile__role='admin').count()
    total_tenants = users.filter(profile__role='tenant').count()
    total_banned = users.filter(is_active=False).count()

    return render(request, 'payment/admin_panel.html', {
        'users': users,
        'total_users': total_users,
        'total_owners': total_owners,
        'total_tenants': total_tenants,
        'total_banned': total_banned,
    })

@login_required(login_url='/login/')
def toggle_ban(request, user_id):
    if request.user.profile.role != 'admin':
        return redirect('owner_dashboard')

    from django.contrib.auth.models import User
    target_user = get_object_or_404(User, id=user_id)

    if target_user != request.user:
        target_user.is_active = not target_user.is_active
        target_user.save()

    return redirect('admin_panel')