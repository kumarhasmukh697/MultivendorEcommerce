from django.contrib import admin
from .models import Order, OrderedFood

class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('food_item', 'quantity', 'price', 'amount')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_status', 'status', 'ordered_date']
    inlines = [OrderedFoodInline]

admin.site.register(Order, OrderAdmin)