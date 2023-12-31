import random
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from carts.models import Cart, CartItem
from .forms import CustomPasswordChangeForm, CustomUserDetailsForm, AddressForm
from django.contrib.auth import update_session_auth_hash
from .models import ShippingAddress, Wallet
from .helpers import render_to_pdf



# Create your views here.

def profile(request):
    success_messages = messages.get_messages(request)
    user_address = ShippingAddress.objects.filter(user=request.user, status=True).first()

    return render(request,'user_profile/profile.html', {'success_messages': success_messages, 'user_address': user_address})




@login_required
def editpassword(request):
    if request.method == 'POST':
        password_change_form = CustomPasswordChangeForm(request.user, request.POST)
        if password_change_form.is_valid():
            user = request.user
            new_password = password_change_form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            messages.success(request, 'Password changed successfully.')
            return redirect('user_authentication:signout')
        else:
            # Include form errors in the context
            return render(request, 'user_profile/password.html', {'password_change_form': password_change_form})


    else:
        password_change_form = CustomPasswordChangeForm(request.user)

    return render(request, 'user_profile/password.html', {'password_change_form': password_change_form})


@login_required
def editdetails(request):
    if request.method == 'POST':
        user_details_form = CustomUserDetailsForm(request.POST, instance=request.user)
        if user_details_form.is_valid():
            user_details_form.save()
            messages.success(request, 'User details updated successfully.')
            return redirect('user_profile:profile')
        else:
            # Include form errors in the context
            return render(request, 'user_profile/details.html', {'user_details_form': user_details_form})

    else:
        user_details_form = CustomUserDetailsForm(instance=request.user)

    return render(request, 'user_profile/details.html', {'user_details_form': user_details_form})

@login_required
def editaddress(request, address_id):
    # Retrieve all addresses for the user
    user_addresses = ShippingAddress.objects.filter(user=request.user)
    
    # Get the specific address for editing
    user_address = get_object_or_404(ShippingAddress, id=address_id)

    if request.method == 'POST':
        # Update the existing address
        address_form = AddressForm(request.POST, instance=user_address)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'User address updated successfully.')
            return redirect('user_profile:addaddress')
    else:
        address_form = AddressForm(instance=user_address)

    return render(request, 'user_profile/edit_address.html', {'address_form': address_form, 'user_address': user_address, 'user_addresses': user_addresses})


@login_required
def addaddress(request):
    # Retrieve all addresses for the user
    user_addresses = ShippingAddress.objects.filter(user=request.user)

    if request.method == 'POST':
        # Create a new address
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'User address added successfully.')
            return redirect('user_profile:addaddress')
        
    else:
        address_form = AddressForm()

    return render(request, 'user_profile/address.html', {'address_form': address_form, 'user_addresses': user_addresses})



@login_required
def deleteaddress(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id)
    address.delete()
    messages.success(request, 'User address deleted successfully.')
    return redirect('user_profile:addaddress')

@login_required
def myorder(request):
    
    order = Cart.objects.filter(user=request.user, complete=True).prefetch_related('cartitem_set__product')
   

    context =   {'order': order, 
                 
                 } 
    return render(request, 'user_profile/orders.html', context)

@login_required
def view_order(request,cart_id):
 
    order = get_object_or_404(Cart.objects.prefetch_related('cartitem_set__product'), id=cart_id)

    context =   {'order': order,                
                 } 
    return render(request, 'user_profile/vieworder.html', context)


@login_required
def cancel_order(request, cart_id):
    cart_item = get_object_or_404(CartItem, id=cart_id)

    if cart_item:      

        cart_item.delivery_status = 'CN'

        cart_item.save()
        messages.success(request, 'Your order is successfully cancelled.')
        if cart_item.order.payment_method == "RAZ" or cart_item.order.payment_method == "WAL":

            refund_amount = cart_item.get_total
            print(refund_amount)
    
            user_wallet = Wallet.objects.get(user=request.user)
            user_wallet.balance += refund_amount
            user_wallet.save()
            print(user_wallet.balance)
        
       
     
    else:

        messages.error(request, 'Invalid order or you are not authorized to cancel this order.')

    return redirect('user_profile:myorder')

@login_required
def generate_invoice(request, cart_id):
    order = get_object_or_404(Cart, id=cart_id)
    invoice_number = str(random.randint(100000, 999999))


    context = {
        'order': order,
        'invoice_number':invoice_number,
       
    }
 

    pdf = render_to_pdf('user_profile/invoice.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename =f"invoice_{order.id}.pdf"
        content = "inline; filename='%s'" % filename
        response['Content-Disposition'] = content
        return response
    else:
        print("Error generating the PDF.")
        return HttpResponse("Error generating the invoice.")
    

@login_required
def wallet(request):
    if request.user.is_authenticated:
        wallet = Wallet.objects.get(user=request.user)       
     
        
    context = {
        'wallet': wallet,
        
    }
    return render(request, 'user_profile/wallet.html',context)




