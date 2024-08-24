from django.contrib import admin
from .models import Medicine
# Register your models here.


class MedicineAdmin(admin.ModelAdmin):
    model = Medicine
    # fields = ['medicine_name', 'description', 'quantity', 'expiry_date']
    list_display = ('medicine_name', 'description', 'quantity', 'expiry_date')

admin.site.register(Medicine, MedicineAdmin)