from django.db import models
from django.contrib.auth.models import User

MONTH_CHOICES = [
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
]

YEAR_CHOICES = [(str(y), str(y)) for y in range(2024, 2030)]

class Payment(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    tenant          = models.ForeignKey(User, on_delete=models.CASCADE)
    unit            = models.CharField(max_length=50)
    period_month    = models.CharField(max_length=10, choices=MONTH_CHOICES, default='January')
    period_year     = models.CharField(max_length=4, choices=YEAR_CHOICES, default='2025')
    rent            = models.DecimalField(max_digits=10, decimal_places=2)
    electric        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    water           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    due_date        = models.DateField()
    paid_date       = models.DateField(null=True, blank=True)

    def utility(self):
        return self.electric + self.water

    def total(self):
        return self.rent + self.utility()

    def period(self):
        return f"{self.period_month} {self.period_year}"

    def __str__(self):
        return f"{self.tenant.username} - {self.period()} - {self.status}"
    
class Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    tenant          = models.ForeignKey(User, on_delete=models.CASCADE)
    title           = models.CharField(max_length=200)
    description     = models.TextField()
    priority        = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    status          = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    submitted_date  = models.DateTimeField(auto_now_add=True)
    updated_date    = models.DateTimeField(auto_now=True)
    admin_notes     = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tenant.username} - {self.title} - {self.priority} - {self.status}"

    class Meta:
        ordering = [
            models.Case(
                models.When(priority='high', then=0),
                models.When(priority='medium', then=1),
                models.When(priority='low', then=2),
                default=3,
            ),
            'submitted_date'
        ]