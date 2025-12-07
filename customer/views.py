from django.shortcuts import render , redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.utils import restrict_vendor, restrict_customer
from accounts.forms import UserForm
from accounts.context_processors import get_user_profile
from accounts.models import User
from accounts.utils import send_verification_email
from django.contrib import messages,auth
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from marketplace.models import AddToCart 
from marketplace.context_processors import get_cart_amounts
from decimal import Decimal 
from datetime import datetime
import json
from django.http import JsonResponse
from orders.models import Order, OrderedFood
import time

# Create your views here.


def registerUser(request):
     if request.POST:
          form = UserForm(request.POST)
          if form.is_valid():
               # user = form.save(commit=False) # form is being ready for save to database but yet not saved
               # user.role = User.CUSTOMER
               # password = form.cleaned_data['password']
               # user.set_password(password)
               # user.save()
               
               #creating user using create_user method
               first_name = form.cleaned_data['first_name']
               last_name = form.cleaned_data['last_name']
               password = form.cleaned_data['password']
               email = form.cleaned_data['email']
               username = form.cleaned_data['username']
               password = form.cleaned_data['password']
               user = User.objects.create_user(first_name=first_name,last_name=last_name,password=password,email=email,username=username)
               user.role = User.CUSTOMER
               user.save()

               #send verification email

               mail_subject = 'Please activate your account'
               email_template = 'accounts/emails/account_verification_email.html'
               send_verification_email(request, user, mail_subject, email_template)    
               
               messages.success(request, 'Please Activate Your Account using link send to your email address!')

               return redirect("registerUser") 

          else:
              print(form.errors)
          
     else:
          form = UserForm()
     
     context = {'form':form,}
     return render(request, 'customer/registerUser.html',context)



@login_required(login_url='login')
@restrict_vendor
def custDashboard(request):
     return render(request,'customer/custDashboard.html')





def profile(request):
     user = request.user
     profile = get_user_profile(request)
     if request.method == 'POST':
          address = request.POST['address']
          first_name = request.POST['first_name']
          last_name = request.POST['last_name']
          profile_picture = request.FILES.get('profile_picture')
          cover_photo = request.FILES.get('cover_photo')
          latitude = request.POST.get('latitude')
          longitude = request.POST.get('longitude')
          city = request.POST.get('city')
          country = request.POST.get('country')
          pin_code = request.POST.get('pin_code')
          state = request.POST.get('state')
          phone_number = request.POST.get('phone_number')
          user.phone_number = phone_number
          profile['user_profile'].address = address
          profile['user_profile'].first_name = first_name
          profile['user_profile'].last_name = last_name
          profile['user_profile'].profile_picture = profile_picture
          profile['user_profile'].cover_photo = cover_photo
          profile['user_profile'].latitude = latitude
          profile['user_profile'].longitude = longitude
          profile['user_profile'].city = city
          profile['user_profile'].country = country
          profile['user_profile'].pin_code = pin_code
          profile['user_profile'].state = state
          profile['user_profile'].save()
          user.save()
          return redirect('profile')

     context = {'user': user, 'user_profile': profile['user_profile']}

     return render(request, 'customer/profile.html', context)


def bookings(request):
    return render(request, 'customer/bookings.html')


# def orders(request):
#     return render(request, 'customer/orders.html')



@login_required(login_url='login')
def checkout(request):
    cart_items = AddToCart.objects.filter(user=request.user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    # Calculate cart amounts using Decimal
    subtotal = sum(Decimal(str(item.price)) * item.quantity for item in cart_items)
    tax = subtotal * Decimal('0.05')  # Convert 5% to Decimal
    grand_total = subtotal + tax
    
    tax_dict = {
        'tax_percentage': 5,
        'tax_amount': tax,
    }

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax_dict': tax_dict,
        'grand_total': grand_total,
        'user': request.user,
        'user_profile': request.user.userprofile,
    }
    return render(request, 'customer/checkout.html', context)


@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaction_id = data.get('transaction_id')
            payment_method = data.get('payment_method')
            status = data.get('status')
            
            # Get cart items
            cart_items = AddToCart.objects.filter(user=request.user)
            if not cart_items:
                return JsonResponse({'status': 'failed', 'message': 'No items in cart'})

            # Generate single order number outside the loop
            order_number = generate_order_number(request.user)
            
            # Group cart items by vendor
            vendor_items = {}
            for item in cart_items:
                if item.product.vendor not in vendor_items:
                    vendor_items[item.product.vendor] = []
                vendor_items[item.product.vendor].append(item)

            # Calculate total amounts for all vendors
            total_subtotal = Decimal('0')
            total_tax = Decimal('0')
            total_grand = Decimal('0')
            for vendor, items in vendor_items.items():
                v_subtotal = sum(item.quantity * Decimal(str(item.price)) for item in items)
                v_tax = v_subtotal * Decimal('0.05')
                total_subtotal += v_subtotal
                total_tax += v_tax
                total_grand += (v_subtotal + v_tax)

            try:
                # Create single order for all vendors
                order = Order.objects.create(
                    order_number=order_number,
                    user=request.user,
                    total=total_subtotal,
                    tax=total_tax,
                    grand_total=total_grand,
                    payment_method=payment_method,
                    payment_id=transaction_id,
                    payment_status='COMPLETED',
                    status='New',
                    first_name=request.user.first_name,
                    last_name=request.user.last_name,
                    phone=request.user.phone_number,
                    email=request.user.email,
                    address=request.user.userprofile.address,
                    city=request.user.userprofile.city,
                    state=request.user.userprofile.state,
                    pin_code=request.user.userprofile.pin_code,
                    total_quantity=sum(item.quantity for item in cart_items)
                )

                # Add all vendors to the order
                for vendor in vendor_items.keys():
                    order.vendors.add(vendor)

                # Create ordered food items for all vendors
                for vendor, items in vendor_items.items():
                    for item in items:
                        OrderedFood.objects.create(
                            order=order,
                            food_item=item.product,
                            quantity=item.quantity,
                            price=Decimal(str(item.price)),
                            amount=item.quantity * Decimal(str(item.price))
                        )

                # Clear the cart after successful order creation
                cart_items.delete()

                return JsonResponse({
                    'status': 'success',
                    'message': 'Order placed successfully',
                    'order_number': order_number
                })

            except Exception as e:
                # If error occurs, delete the order
                if 'order' in locals():
                    order.delete()
                return JsonResponse({
                    'status': 'failed',
                    'message': f'Failed to create order: {str(e)}'
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'failed',
                'message': f'Error processing request: {str(e)}'
            })

    return JsonResponse({
        'status': 'failed',
        'message': 'Invalid request method'
    })

def generate_order_number(user):
    # Get current timestamp
    # take some time to genreate timestap using time.sleep
    time.sleep(5)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = f'{user.id}{timestamp}'
    return order_number


@login_required(login_url='login')
def order_complete(request, order_number):
    try:
        # Get the order
        order = Order.objects.get(order_number=order_number, user=request.user)
        
        # Get all ordered food items grouped by vendor
        vendors_with_items = {}
        ordered_foods = OrderedFood.objects.filter(order=order)
        
        for food in ordered_foods:
            vendor = food.food_item.vendor
            if vendor not in vendors_with_items:
                vendors_with_items[vendor] = []
            vendors_with_items[vendor].append(food)

        context = {
            'order': order,
            'vendors_with_items': vendors_with_items.items(),
            'subtotal': order.total,
            'tax': order.tax,
            'grand_total': order.grand_total,
            'transaction_id': order.payment_id
        }
        
        return render(request, 'orders/order_complete.html', context)
    
    except Order.DoesNotExist:
        return redirect('custDashboard')
    except Exception as e:
        print('Error:', e)
        return redirect('custDashboard')