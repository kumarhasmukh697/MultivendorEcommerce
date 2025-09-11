from django.db import models
from accounts.models import User
from menu.models import FoodItem

# Create your models here.


class AddToCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product} - {self.quantity} @ {self.price}"
    
    class Meta:
        verbose_name = "Add to Cart"
        verbose_name_plural = "Add to Cart" 