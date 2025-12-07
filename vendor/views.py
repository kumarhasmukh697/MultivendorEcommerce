from accounts.forms import UserForm
from django.shortcuts import get_object_or_404
from vendor.models import Vendor
from accounts.models import User,UserProfile
from .forms import VendorForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST  # Add this line
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from accounts.utils import restrict_customer
from vendor.models import Vendor,OpenHours
from django.utils.text import slugify
from django.utils import timezone
from accounts.context_processors import get_vendor,get_user_profile
import json
from orders.models import Order,OrderedFood
from django.db.models import Q






def registerVendor(request):
     if request.POST:
          form = UserForm(request.POST)
          v_form = VendorForm(request.POST,request.FILES)

          if form.is_valid() and v_form.is_valid():
               first_name = form.cleaned_data['first_name']
               last_name = form.cleaned_data['last_name']
               email = form.cleaned_data['email']
               username = form.cleaned_data['username']
               password = form.cleaned_data['password']

               user = User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
               user.role = User.VENDOR
               user.save()
               vendor = v_form.save(commit=False)
               user_profile = UserProfile.objects.get(user=user)
               vendor.user = user
               vendor.user_profile = user_profile
               vendor.vendor_slug = v_form.cleaned_data['vendor_name']
               vendor.save()

               mail_subject = 'Please activate your account'
               email_template = 'accounts/emails/account_verification_email.html'
               send_verification_email(request, user, mail_subject, email_template) 

               messages.success(request, 'Please Activate Your Account using link send to your email address!')
               return redirect('registerVendor')
          
          else:
               print(form.errors)
               print(v_form.errors)
         
     else:
          form = UserForm()
          v_form = VendorForm()

     context = {"form":form,"v_form":v_form}
     return render(request,'vendor/registerVendor.html',context) 


@login_required(login_url='login')
@restrict_customer
def vendorDashboard(request):
     return render(request,'vendor/vendorDashboard.html')





@login_required(login_url='login')
def vprofile(request):
     profile = get_object_or_404(UserProfile, user=request.user)
     vendor = get_object_or_404(Vendor, user=request.user)
    

     if request.method == 'POST':
          profile_update = {
            'profile_picture': request.FILES.get('profile_picture'),
            'cover_photo': request.FILES.get('cover_photo'),
            'address': request.POST.get('address'),
            'country': request.POST.get('country'),
            'state': request.POST.get('state'),
            'city': request.POST.get('city'),
            'pin_code': request.POST.get('pin_code'),
            'latitude': request.POST.get('latitude'),
            'longitude': request.POST.get('longitude'),
          }

          vendor_update = {
            'vendor_name': request.POST.get('restaurant_name'),
            'vendor_license': request.FILES.get('license'),
          }

        # Update profile picture and cover photo only if new files are uploaded
          if profile_update['profile_picture']:
               profile.profile_picture = profile_update['profile_picture']
          if profile_update['cover_photo']:
               profile.cover_photo = profile_update['cover_photo']

        # Update other profile fields
          for key, value in profile_update.items():
               if key not in ['profile_picture', 'cover_photo'] and value:
                    setattr(profile, key, value)
          profile.save()

        # Update vendor fields
          if vendor_update['vendor_license']:
               vendor.vendor_license = vendor_update['vendor_license']
          if vendor_update['vendor_name']:
               vendor.vendor_name = vendor_update['vendor_name']
          vendor.save()

          messages.success(request, 'Restaurant profile updated successfully!')
          return redirect('vprofile')

     context = {
        'profile': profile,
        'vendor': vendor,
     }
     return render(request, 'vendor/vprofile.html', context)     


@login_required(login_url='login')
@restrict_customer
def menu_builder(request):
    # Get vendor
    vendor = get_object_or_404(Vendor, user=request.user)
    
    # Get categories for this vendor
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@restrict_customer
def fooditems_by_category(request, pk=None):
    vendor = get_object_or_404(Vendor, user=request.user)
    category = get_object_or_404(Category, pk=pk)
    
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url='login')
@restrict_customer
def add_category(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = vendor
            category.save()
            messages.success(request, 'Category added successfully.')
            return redirect('menu_builder')
        else:
            pass


    else:
        form = CategoryForm()
    
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)


def edit_category(request, pk):
    vendor = get_object_or_404(Vendor, user=request.user)
    category = get_object_or_404(Category, pk=pk, vendor=vendor)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('menu_builder')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)



@login_required(login_url='login')
@restrict_customer
def delete_category(request, pk):
    vendor = get_object_or_404(Vendor, user=request.user)
    category = get_object_or_404(Category, pk=pk, vendor=vendor)
    
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('menu_builder')   


@login_required(login_url='login')
@restrict_customer
def add_fooditem(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
       
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
           
            fooditem = form.save(commit=False)
            fooditem.vendor = vendor
            fooditem.slug = slugify(form.cleaned_data['food_title'])
            fooditem.save()
            
            messages.success(request, 'Food item added successfully.')
            return redirect('fooditems_by_category', pk=fooditem.category.pk)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
          # Filter the categories queryset to show only current vendor's categories
        form.fields['category'].queryset = Category.objects.filter(vendor=vendor)
    
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_fooditem.html', context)


@login_required(login_url='login')
@restrict_customer
def edit_fooditem(request, pk):
    vendor = get_object_or_404(Vendor, user=request.user)
    fooditem = get_object_or_404(FoodItem, pk=pk, vendor=vendor)
    
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=fooditem)
        if form.is_valid():
            fooditem = form.save(commit=False)
            fooditem.slug = slugify(form.cleaned_data['food_title'])
            fooditem.save()
            messages.success(request, 'Food item updated successfully.')
            return redirect('fooditems_by_category', pk=fooditem.category.pk)
    else:
        form = FoodItemForm(instance=fooditem)
        form.fields['category'].queryset = Category.objects.filter(vendor=vendor)
       
    
    context = {
        'form': form,
        'fooditem': fooditem,
    }
    return render(request, 'vendor/edit_fooditem.html', context)


@login_required(login_url='login')
@restrict_customer
def delete_fooditem(request, pk):
    vendor = get_object_or_404(Vendor, user=request.user)
    fooditem = get_object_or_404(FoodItem, pk=pk, vendor=vendor)
    category_id = fooditem.category.id  # Store category id before deletion
    
    fooditem.delete()
    messages.success(request, 'Food item deleted successfully!')
    return redirect('fooditems_by_category', pk=category_id)



@login_required
def opening_hours(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    opening_hours = OpenHours.objects.filter(vendor=vendor).order_by('day_of_week')
    
    # Get current time info
    now = timezone.now()
    current_day = now.strftime('%A')
    current_time = now.time()
    
    hours_status = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for oh in opening_hours:
        status = "Holiday" if oh.is_closed else "Open"
        if oh.day_of_week == current_day and not oh.is_closed:
            # Convert string times to time objects
            if oh.opening_time and oh.closing_time:
                if isinstance(oh.opening_time, str):
                    oh_opening = datetime.strptime(oh.opening_time, '%H:%M').time()
                else:
                    oh_opening = oh.opening_time
                    
                if isinstance(oh.closing_time, str):
                    oh_closing = datetime.strptime(oh.closing_time, '%H:%M').time()
                else:
                    oh_closing = oh.closing_time
                    
                if oh_opening <= current_time <= oh_closing:
                    status = "Shop Open"
                else:
                    status = "Closed"
                    
        hours_status.append({
            'id': oh.id,
            'day': oh.day_of_week,
            'opening_time': oh.opening_time.strftime('%H:%M') if oh.opening_time else '',
            'closing_time': oh.closing_time.strftime('%H:%M') if oh.closing_time else '',
            'is_closed': oh.is_closed,
            'status': status
        })

    context = {
        'opening_hours': opening_hours,
        'days': days,
        'hours_status': hours_status,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'hours_status': hours_status})
    return render(request, 'vendor/opening_hours.html', context)


from datetime import datetime  # Add this import at the top

@login_required
@require_POST
def add_opening_hour(request):
    try:
        data = json.loads(request.body)
        vendor = get_object_or_404(Vendor, user=request.user)
        
        # Get current time info
        now = timezone.now()
        current_day = now.strftime('%A')
        current_time = now.time()
        
        # Check if hours already exist for this day
        if OpenHours.objects.filter(vendor=vendor, day_of_week=data.get('day')).exists():
            return JsonResponse({
                'success': False,
                'error': f'Hours already exist for {data.get("day")}'
            })

        # Convert string times to time objects
        opening_time = None
        closing_time = None
        if not data.get('is_closed'):
            opening_time = datetime.strptime(data.get('opening_time'), '%H:%M').time()
            closing_time = datetime.strptime(data.get('closing_time'), '%H:%M').time()

        # Create new opening hours
        opening_hour = OpenHours.objects.create(
            vendor=vendor,
            day_of_week=data.get('day'),
            opening_time=opening_time,
            closing_time=closing_time,
            is_closed=data.get('is_closed', False)
        )

        # Determine status
        status = "Holiday"
        if not opening_hour.is_closed:
            if opening_hour.day_of_week == current_day:
                if opening_time <= current_time <= closing_time:
                    status = "Shop Open"
                else:
                    status = "Closed"
            else:
                status = "Open"

        return JsonResponse({
            'success': True,
            'id': opening_hour.id,
            'day': opening_hour.day_of_week,
            'opening_time': opening_time.strftime('%H:%M') if opening_time else '',
            'closing_time': closing_time.strftime('%H:%M') if closing_time else '',
            'is_closed': opening_hour.is_closed,
            'status': status
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def delete_opening_hour(request):
    data = json.loads(request.body)
    oh_id = data.get('id')
    try:
        oh = OpenHours.objects.get(id=oh_id, vendor__user=request.user)
        oh.delete()
        return JsonResponse({'success': True})
    except OpenHours.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'})




@login_required(login_url='login')
@restrict_customer
def orders(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    orders = Order.objects.filter(vendors=vendor).order_by('-ordered_date')  # Changed from created_at to ordered_date
    
    context = {
        'orders': orders,
        'vendor': vendor,
    }
    return render(request, 'vendor/orders.html', context)


def earnings(request):
    return render(request, 'vendor/earnings.html')



@login_required(login_url='login')
@restrict_customer
def particular_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, vendors__user=request.user)
    orderfood = OrderedFood.objects.filter(order=order)
    context = {
        'order': order,
        'orderfood': orderfood
    }
    return render(request, 'vendor/particular_order.html', context)