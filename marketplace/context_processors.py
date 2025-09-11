from .models import AddToCart

def get_cart_amounts(request):
    if request.user.is_authenticated:
        cart_items = AddToCart.objects.filter(user=request.user)
        subtotal = 0
        tax = 0
        grand_total = 0
        
        for item in cart_items:
            subtotal += (item.price * item.quantity)
        
        # Calculate tax (assuming 5% tax)
        tax = subtotal * 0.05
        
        # Calculate grand total
        grand_total = subtotal + tax
        
        tax_dict = {
            'tax_percentage': 5,
            'tax_amount': tax,
        }
        
        return {
            'subtotal': subtotal,
            'tax_dict': tax_dict,
            'grand_total': grand_total,
        }
    return {'subtotal': 0, 'tax_dict': {'tax_percentage': 0, 'tax_amount': 0}, 'grand_total': 0}