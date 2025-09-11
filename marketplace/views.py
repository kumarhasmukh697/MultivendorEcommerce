from django.shortcuts import render,get_object_or_404
from django.db import models 
from vendor.models import Vendor
from menu.models import FoodItem, Category
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AddToCart
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models import Q

# Create your views here.
def marketplace(request):
    food = FoodItem.objects.all()
    vendor = Vendor.objects.all()
    count = len(vendor)
    context = {
        'vendor': vendor,
        'count':count,
        'food': food,
    }
    return render(request, 'marketplace/listing.html', context)


def listing(request,vendor_slug):
    # This view can be used to display a list of products or vendors
    # For now, it just renders a simple template
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    fooditems = FoodItem.objects.filter(vendor=vendor).order_by('created_at')

    
    context = {
        'vendor': vendor,
        'categories': categories,
        'fooditems': fooditems,
    }
    return render(request, 'marketplace/listing_detail.html', context)




@login_required
def cart(request):
    cart_items = AddToCart.objects.filter(user=request.user)
    total = 0
    cart_count = 0
    for item in cart_items:
       total = total + (item.price) * item.quantity
       cart_count += item.quantity
    # Optionally, get categories and fooditems for sidebar if needed
    # categories = Category.objects.filter(fooditem__in=[item.product for item in cart_items]).distinct()
    context = {
        'cart_items': cart_items,
        'total':total,
        'cart_count': cart_count,
       
    }
    return render(request, 'marketplace/cart.html', context)

# @login_required
# def cart(request):
#     cart_items = AddToCart.objects.filter(user=request.user).select_related('product__vendor')
#     total = 0
#     cart_count = 0
    
#     # Group cart items by vendor
#     vendor_items = {}
#     for item in cart_items:
#         total += item.price * item.quantity
#         cart_count += item.quantity
        
#         # Group items by vendor
#         vendor = item.product.vendor
#         if vendor not in vendor_items:
#             vendor_items[vendor] = []
#         vendor_items[vendor].append(item)

#     context = {
#         'vendor_items': vendor_items,
#         'total': total,
#         'cart_count': cart_count,
#     }
#     return render(request, 'marketplace/cart.html', context)


@csrf_exempt
@login_required
def add_to_cart(request, item_id):
    if request.method == 'POST':
        food_item = FoodItem.objects.get(id=item_id)
        cart_item, created = AddToCart.objects.get_or_create(
            user=request.user,
            product=food_item,
            defaults={'quantity': 1, 'price': food_item.price}
        )
        # If the item was already in the cart, increment the quantity
        # If it was newly created, the quantity is already set to 1
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        cart_count = AddToCart.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0
        return JsonResponse({'quantity': cart_item.quantity, 'cart_count': cart_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
@login_required
def remove_from_cart(request, item_id ):
    if request.method == 'POST':
        food_item = FoodItem.objects.get(id=item_id)
        try:
            cart_item = AddToCart.objects.get(user=request.user, product=food_item)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                quantity = cart_item.quantity
            else:
                cart_item.delete()
                quantity = 0
        except AddToCart.DoesNotExist:
            quantity = 0
        cart_count = AddToCart.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0
        return JsonResponse({'quantity': quantity, 'cart_count': cart_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)




from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

def search(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    distance = request.GET.get('distance', '')
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')

    vendors = Vendor.objects.all()

    # ... existing query and location filtering ...

    # Filter by distance if coordinates are provided
    if latitude and longitude and distance and distance != "more":
        try:
            user_location = Point(float(longitude), float(latitude), srid=4326)
            vendors = vendors.filter(
                user_profile__location__distance_lte=(user_location, D(km=float(distance)))
            )
        except Exception as e:
            pass  # Optionally log the error

    context = {
        'vendors': vendors,
        'query': query,
        'location': location,
        'distance': distance,
    }
    return render(request, 'home.html', context)