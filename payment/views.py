from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Payment
from .utils import check_overdue_payments
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
    if request.user.profile.role != 'admin':
        return redirect('payment_history')
    
    check_overdue_payments()
    
    payments = Payment.objects.all().order_by('-due_date')
    return render(request, 'payment/admin_history.html', {
        'payments': payments
    })

def payment_success(request):
    return render(request, 'payment/success.html')

@login_required(login_url='/login/')
def tenant_payment_dashboard(request):
    check_overdue_payments()  # ← add this line

    unpaid = Payment.objects.filter(
        tenant=request.user,
        status='unpaid'
    ).order_by('due_date')

    overdue = Payment.objects.filter(
        tenant=request.user,
        status='overdue'
    ).order_by('due_date')

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

# Tenant — submit complaint
@login_required(login_url='/login/')
def complaint_submit(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')

        Complaint.objects.create(
            tenant=request.user,
            title=title,
            description=description,
            priority=priority,
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