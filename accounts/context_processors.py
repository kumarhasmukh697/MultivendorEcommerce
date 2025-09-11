from django.conf import settings
from vendor.models import Vendor
from accounts.models import UserProfile
from marketplace.models import AddToCart


def get_vendor(request):
    vendor = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
        except:
            vendor = None
    return dict(vendor=vendor)


def get_user_profile(request):
    user_profile = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None
    return dict(user_profile=user_profile)    


def google_api_key(request):
    return {
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY
    }


def paypal_client_id(request):
    return {
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID  # Changed to match settings
    }


def get_cart_count(request):
    cart_count = 0
    total = 0
    if hasattr(request, 'user') and request.user.is_authenticated:
        cart_items = AddToCart.objects.filter(user=request.user)
        for item in cart_items:
            cart_count += item.quantity
            total += (item.price * item.quantity)
    return dict(cart_count=cart_count, cart_total=total)
   