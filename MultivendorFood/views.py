from django.shortcuts import render
from vendor.models import Vendor



def home(request):
    vendor = Vendor.objects.all()  # Fetch all vendors
    context = {'vendor': vendor,}
    return render(request, 'home.html', context)