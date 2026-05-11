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