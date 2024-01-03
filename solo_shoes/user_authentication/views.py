from datetime import timedelta
from decimal import Decimal
from itertools import count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.db.models import Q
import random
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from django.views.decorators.cache import never_cache
from custom_admin_panel.models import Category, Product
from user_profile.models import Wallet
from store.models import Offer, OfferCategory
import random




def home(request):
      products = Product.objects.all()
      for product in products:
        now = timezone.now()
        
        product.offer = Offer.objects.filter(
        Q(product=product) & Q(date_start__lte=now, date_end__gt=now)).first()

        product.category.offer = OfferCategory.objects.filter(
        Q(category=product.category) & Q(date_start__lte=now, date_end__gt=now)).first()
        
        if product.offer and product.category.offer:
            if product.offer.discount_percentage > product.category.offer.discount_percentage:
                discount_percentage = Decimal(product.offer.discount_percentage) / Decimal(100)
                product.discounted_price = product.price - (product.price * discount_percentage)
            else:
                discount_percentage = Decimal(product.category.offer.discount_percentage) / Decimal(100)
                product.discounted_price = product.price - (product.price * discount_percentage)
        elif product.category.offer:
            discount_percentage = Decimal(product.category.offer.discount_percentage) / Decimal(100)
            product.discounted_price = product.price - (product.price * discount_percentage)
        elif product.offer:
            discount_percentage = Decimal(product.offer.discount_percentage) / Decimal(100)
            product.discounted_price = product.price - (product.price * discount_percentage)
             
        else:
            product.discounted_price = None


      context = {
          'products' : products,

      }
      return render(request, 'user_authentication/index.html' , context)

# def search_suggestions(request):
#     print("Search product in home page")
#     term = request.GET.get('term', '')
#     suggestions = Product.objects.filter(product_name__icontains=term)[:5] 
#     data = [{'label': product.product_name, 'value': product.product_name, 'url': reverse('store:product', args=[product.id])} for product in suggestions]
#     return JsonResponse(data, safe=False)

# In your views.py

def search_results(request):
    
    query = request.GET.get('q', '')
    results = []

    if query:
        print("ENTERED INTO SEARCH")
        results = list(Product.objects.filter(product_name__icontains=query).values('product_name')[:5])


    return JsonResponse(results, safe=False)




def register(request):
    if request.method == "POST":
        first_name = request.POST.get('register-firstname')
        last_name = request.POST.get('register-lastname')
        username = request.POST.get('register-username')
        email = request.POST.get('register-email', '')        
        password = request.POST.get('register-password')
        password1 = request.POST.get('register-password1')

        try:
            # Attempt to create the user
            myuser = User.objects.create_user(username, email, password)
            # new_user = CustomUser.objects.create(username='new_user', referral_code=generate_referral_code())

            myuser.first_name = first_name
            myuser.last_name = last_name
            myuser.is_active = False
            myuser.save()

            request.session['email'] = email

            send_otp(request)
            
            return render(request, 'user_authentication/otp.html', {'email': email})
        except IntegrityError:
            # Handle the case where the username is not unique
            print("Error")
            return render(request, 'user_authentication/login.html', {'error_message': 'Username already exists'})

       
    
    return render(request, 'user_authentication/login.html')




def loginn(request):
   
    if request.user.is_authenticated:
         return redirect('user_authentication:home')

    if request.method == 'POST':
      
        username = request.POST['signin-username']
        pass1 = request.POST['signin-password']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            
            return redirect('user_authentication:home')
        else:
           
            messages.error(request, 'Invalid Credentials!!')
            return redirect('user_authentication:login')

    return render(request, 'user_authentication/login.html')

@never_cache
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')  

        is_email_exist = User.objects.filter(email=email).exists()

        if is_email_exist:

            # Store the email in the session
            request.session['email'] = email

            # Call the send_otp function to send the OTP
            send_pswrd_otp(request)
            return render(request, 'user_authentication/paswrd_otp.html', {'email': email})        

        else:
            messages.error(request, 'Invalid Email!!')
            return redirect('user_authentication:forgot_password')

    return render(request,'user_authentication/forgot_paswrd.html')
def resend_otp(request):
    send_pswrd_otp(request)
    # return redirect('user_authentication:password_otp')
    return render(request, 'user_authentication/paswrd_otp.html')

def resend_register_otp(request):
    send_otp(request)
    
    return render(request, 'user_authentication/otp.html')


@never_cache
def password_otp_verification(request):
    if request.method == 'POST':
        otp_ = request.POST.get("otp")
        
        # Get the OTP generation time from the session
        otp_generated_time = request.session.get("otp_generated_time")

        # Check if OTP generation time exists and is within the last 1 minute
        if otp_generated_time and timezone.now() - timezone.datetime.fromisoformat(otp_generated_time) < timedelta(minutes=1):
            if otp_ == request.session["otp"]:
                email = request.session['email']
                user = User.objects.get(email = email)
                user.is_active = True
                user.save()
                # login(request, user)
                # messages.info(request, 'Password is reset successfully...')
                return redirect('user_authentication:set_password')  # Assuming 'home:index' is the URL name for the home page
            else:
                messages.error(request, "OTP doesn't match")
        else:
            messages.error(request, "OTP has expired. Please request a new OTP.")
            
        return render(request, 'user_authentication/paswrd_otp.html')

from django.contrib.auth.hashers import make_password

def set_password(request):
    if request.method == 'POST':
        new_password = request.POST['password1']

        # Check if 'email' is in the session
        if 'email' in request.session:
            email = request.session['email']
            # Use get() with a default value to avoid raising DoesNotExist exception
            user = User.objects.get(email=email)
            # Use make_password to properly hash the new password
            user.password = make_password(new_password)
            user.save()
            
            # Remove 'email' from session after setting the password
            del request.session['email']

            # Redirect to the login page or any other desired page
            return render(request, 'user_authentication/login.html')
    return render(request, 'user_authentication/set_pswrd.html')  # Handle the case when 'email' is not in the session


@never_cache
def otp_verification(request):
    if request.method == 'POST':
        otp_ = request.POST.get("otp")
        
        # Get the OTP generation time from the session
        otp_generated_time = request.session.get("otp_generated_time")

        # Check if OTP generation time exists and is within the last 1 minute
        if otp_generated_time and timezone.now() - timezone.datetime.fromisoformat(otp_generated_time) < timedelta(minutes=1):
            if otp_ == request.session["otp"]:
                email = request.session['email']
                user = User.objects.get(email = email)
                user.is_active = True
                user.save()
                login(request, user)
                messages.info(request, 'Signed in successfully...')
                return redirect('user_authentication:home')  # Assuming 'home:index' is the URL name for the home page
            else:
                messages.error(request, "OTP doesn't match")
        else:
            messages.error(request, "OTP has expired. Please request a new OTP.")
            
        return render(request, 'userauths/otp.html')


def send_otp(request):
    s = ''.join(str(random.randint(0, 9)) for _ in range(4))
    request.session["otp"] = s
   
    request.session["otp_generated_time"] = timezone.now().isoformat()
    send_mail("OTP for sign IN", s, "sininasihabudheen@gmail.com", [request.session['email']], fail_silently=False)

def send_pswrd_otp(request):
    s = ''.join(str(random.randint(0, 9)) for _ in range(4))
    request.session["otp"] = s
   
    request.session["otp_generated_time"] = timezone.now().isoformat()
    send_mail("OTP for set new password..", s, "sininasihabudheen@gmail.com", [request.session['email']], fail_silently=False)
     

@never_cache
def signout(request):
    logout(request)
    messages.success(request, "You are Logged out successffully..")
    return redirect('user_authentication:home')

