from django.db import models
from accounts.models import User
from vendor.models import Vendor
from menu.models import FoodItem
from django.utils import timezone
from datetime import datetime

class Order(models.Model):


    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('RazorPay', 'RazorPay'),
    )

    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS = (
        ('PENDING', 'PENDING'),
        ('COMPLETED', 'COMPLETED'),
        ('FAILED', 'FAILED'),
    )

    order_number = models.CharField(max_length=30, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='PENDING')
    payment_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=25, choices=PAYMENT_METHOD)

    # Customer Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)

    # Order Information
    total_quantity = models.IntegerField()
    ordered_date = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number} by {self.user.email}"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


    def save(self, *args, **kwargs):
        if not self.ordered_date:
            self.ordered_date = timezone.localtime()
        super(Order, self).save(*args, **kwargs)    


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ordered_foods')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_item.food_title} - {self.quantity}"