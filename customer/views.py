from django.shortcuts import render , redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.utils import restrict_vendor, restrict_customer
from accounts.forms import UserForm
from accounts.context_processors import get_user_profile
from accounts.models import User
from accounts.utils import send_verification_email
from django.contrib import messages,auth

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


def orders(request):
    return render(request, 'customer/orders.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from marketplace.models import AddToCart  # Add this import
from marketplace.context_processors import get_cart_amounts  # Add this import

from decimal import Decimal  # Add this import at the top

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



# filepath: c:\Django_project\MultivendorFood\customer\views.py

@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
        # Get payment method and transaction ID
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')
        
        if payment_method and transaction_id:
            # Process the order here
            # Clear the cart
            cart_items = AddToCart.objects.filter(user=request.user)
            cart_items.delete()
            
            return redirect('order_complete')
    return redirect('checkout')





@login_required(login_url='login')
def order_complete(request):
    transaction_id = request.GET.get('transaction_id')
    if not transaction_id:
        return redirect('marketplace')
        
    cart_items = AddToCart.objects.filter(user=request.user)
    cart_items.delete()  # Clear the cart
    
    return render(request, 'customer/order_complete.html', {
        'transaction_id': transaction_id
    })