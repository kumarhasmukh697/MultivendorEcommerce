from django.contrib import admin
from .models import Vendor , OpenHours

# Register your models here.

class VendorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'vendor_slug': ('vendor_name',)}

class OpenHoursAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'day_of_week', 'opening_time', 'closing_time', 'is_closed')
    list_filter = ('vendor', 'day_of_week', 'is_closed')

admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpenHours, OpenHoursAdmin)
