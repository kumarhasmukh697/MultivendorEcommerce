from django.shortcuts import render,redirect
from .forms import UserForm
from vendor.forms import VendorForm
from django.urls import reverse
from .models import User,UserProfile
from django.contrib import messages,auth
from django.contrib.auth import authenticate,login,logout
from .utils import detectUser
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .utils import send_verification_email
from django.contrib.auth.decorators import login_required
from .utils import restrict_vendor, restrict_customer



# Create your views here.

def login(request):
     if request.user.is_authenticated:
          messages.warning(request,'You are already logged in!')
          return redirect(detectUser(request.user))
     
     elif request.method == 'POST':
          email = request.POST['email']
          password = request.POST['password']
         
          user = auth.authenticate(email=email,password=password)

          if user is not None:
               auth.login(request,user)
               messages.success(request,"You are logged in")
               return redirect(detectUser(request.user))
              
          else:
               messages.warning(request,"Invalid Login credentials")
               return redirect('login')

     return render(request,'accounts/login.html')



def logout(request):
     auth.logout(request)
     messages.info(request,'You are logged out')
     return redirect('login')
     

@login_required(login_url='login')
def myAccount(request):
     user = request.user
     redirectUrl = detectUser(user)
     return redirect(redirectUrl)




def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        print(user)
        print(uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')
    


def forgot_password(request): 
     if request.method == 'POST':
          email = request.POST['email']

          if User.objects.filter(email=email).exists():
               user = User.objects.get(email__exact = email)
               print(user)
               
               # send reset password email
               mail_subject = 'Reset Your Password'
               email_template = 'accounts/emails/reset_password_email.html'
               send_verification_email(request, user, mail_subject, email_template)

               messages.success(request, 'Password reset link has been sent to your email address.')
               return redirect('login')
          
          else:
               messages.error(request, 'Account does not exist')
               return redirect('forgot_password')
         

     return render(request,'accounts/forgot_password.html')   



def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
     try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

     if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
     else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')
     


def reset_password(request):
     if request.method == 'POST':
          print(request.POST)
          password = request.POST['password']
          confirm_password = request.POST['confirm_password']

          if password == confirm_password:
               pk = request.session.get('uid')
               user = User.objects.get(pk=pk)
               user.set_password(password)
               user.is_active = True
               user.save()
               messages.success(request, 'Password reset successful')
               return redirect('login')
          else:
               messages.warning(request, 'Password do not match!')
               return redirect('reset_password')
     return render(request, 'accounts/reset_password.html')     



from django.shortcuts import get_object_or_404
from vendor.models import Vendor

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
     return render(request, 'accounts/vprofile.html', context)