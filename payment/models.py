from django.db import models

class Payment(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    tenant_name = models.CharField(max_length=100)
    unit        = models.CharField(max_length=50)
    period      = models.CharField(max_length=50)
    rent        = models.DecimalField(max_digits=10, decimal_places=2)
    utility     = models.DecimalField(max_digits=10, decimal_places=2)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    due_date    = models.DateField()
    paid_date   = models.DateField(null=True, blank=True)

    def total(self):
        return self.rent + self.utility

    def __str__(self):
        return f"{self.tenant_name} - {self.period} - {self.status}"