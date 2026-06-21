from django.contrib import admin
from .models import Payment, Complaint, RentalContract

admin.site.register(Payment)
admin.site.register(Complaint)

class RentalContractAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'unit', 'start_date', 'duration_months', 'monthly_rent']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.generate_payments()

admin.site.register(RentalContract, RentalContractAdmin)