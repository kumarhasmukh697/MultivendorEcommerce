from django.contrib import admin

# Register your models here.
from .models import AddToCart
@admin.register(AddToCart)
class AddToCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'created_at']
    search_fields = ['user__username', 'product__name']
    list_filter = ['created_at']
