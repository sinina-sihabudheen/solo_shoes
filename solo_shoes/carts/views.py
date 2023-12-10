from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
# from django.urls import reverse
from custom_admin_panel.models import Product
from carts.models import Cart, CartItem, ShoppingCart, Whishlist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from store.models import Offer, OfferCategory
from user_profile.models import ShippingAddress
from django.contrib.auth.decorators import login_required
from user_profile.forms import AddressForm
# from django.db import transaction 
from decimal import Decimal
from .models import Cart, CartItem, Coupon



def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        request.session.save()
        cart = request.session.session_key
        shopping_cart, created = ShoppingCart.objects.get_or_create(session_key=cart)
        
        if request.user.is_authenticated:
            user_cart, _ = Cart.objects.get_or_create(user=request.user, shopping_cart=shopping_cart)
        
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        
        messages.error(request, "Product not found.")
        return redirect('carts:carts')
    
    current_user = request.user
    
    if current_user.is_authenticated:
        
        cart, _ = Cart.objects.get_or_create(user=current_user, complete = False)
        if not cart.shopping_cart:
            cart.shopping_cart, created = ShoppingCart.objects.get_or_create(session_key=request.session.session_key)
            cart.save()
    

    try:
        cart_item = CartItem.objects.get(order=cart, product=product)
        cart_item.quantity += 1
        product.stock-=1
        product.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(order=cart, product=product, quantity=1)    
        cart_item.save()   
        product.stock -= 1
        product.save()
        
    try:
         wishlist = Whishlist.objects.get(user=request.user)
    except ObjectDoesNotExist:
   
        wishlist = Whishlist(user=request.user)
        wishlist.save()

    wishlist.products.remove(product)
    wishlist.save()
    messages.success(request, f"{product.product_name} added to the cart.")

    return redirect('carts:carts')

def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    current_user = request.user

    if current_user.is_authenticated:
        # If the user is authenticated, associate the Cart with the user's shopping cart
        cart, _ = Cart.objects.get_or_create(user=current_user, complete = False)
        if not cart.shopping_cart:
            cart.shopping_cart, created = ShoppingCart.objects.get_or_create(session_key=request.session.session_key)
            cart.save()
    else:
        # If the user is not authenticated, associate the Cart with the session's shopping cart
        session_key = _cart_id(request)
        shopping_cart = ShoppingCart.objects.get(session_key=session_key)
        cart, _ = Cart.objects.get_or_create(shopping_cart=shopping_cart)

    # Attempt to get the CartItem related to the product
    try:
        cart_item = CartItem.objects.get(order=cart, product=product)
        
        # Increment the stock of the product and save it
        product.stock += cart_item.quantity
        product.save()

        # Remove the CartItem from the cart
        cart_item.delete()
    except CartItem.DoesNotExist:
        # If the CartItem doesn't exist, do nothing
        pass

    return redirect('carts:carts')




def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get(user=request.user, complete=False)

        cart_item, created = CartItem.objects.get_or_create(order=cart, product__id=product_id)
        
        if not created:
            if action == 'increment':
                if product.stock > 0:
                    cart_item.quantity += 1
                    product.stock -= 1
                    product.save()
            elif action == 'decrement':
                cart_item.quantity -= 1
                product.stock += 1
                product.save()

                if cart_item.quantity <= 0:
                    cart_item.delete()

            cart_item.save()
            messages.success(request, 'Cart updated successfully.')

    return redirect('carts:carts')

def carts(request, total=0, quantity=0):
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user, complete = False)
            cart_items = CartItem.objects.filter(order=cart)

            for cart_item in cart_items:
                cart_item.offer = Offer.objects.filter(product=cart_item.product).first()
                product_category = cart_item.product.category  
                cart_item.product.category.offer = OfferCategory.objects.filter(category=product_category).first()
                
                if cart_item.product.offer and cart_item.product.category.offer:
                    discount_percentage = max(cart_item.product.offer.discount_percentage, cart_item.product.category.offer.discount_percentage)
                elif cart_item.product.category.offer:
                    discount_percentage = cart_item.product.category.offer.discount_percentage
                elif cart_item.product.offer:
                    discount_percentage = cart_item.product.offer.discount_percentage
                else:
                    discount_percentage = 0
                
                if discount_percentage > 0:
                    discount_factor = Decimal(discount_percentage) / Decimal(100)
                    cart_item.discounted_price = cart_item.product.price - (cart_item.product.price * discount_factor)
                else:
                    cart_item.discounted_price = None

                

                
                # Update total and quantity
                if cart_item.discounted_price is not None:
                    total += cart_item.discounted_price * cart_item.quantity
                else:
                    total += cart_item.product.price * cart_item.quantity
                
                quantity += cart_item.quantity

    except ObjectDoesNotExist:
        cart_items = []

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'cart' : cart,
    }

    return render(request, 'carts/cart.html', context)


def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user, complete = False)
        cart_items = CartItem.objects.filter(order=cart)
        user_address = ShippingAddress.objects.filter(user=request.user, status=True).first()
        print(user_address)

        # Calculate total and quantity
        total = 0
        quantity = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity


      

        user_addresses = ShippingAddress.objects.filter(user=request.user)
       

        context = {
            'cart': cart,
            'user_address': user_address,
            'user_addresses': user_addresses,
            'cart_items': cart_items,
            'total': total,
            'quantity': quantity,
            
        }

        return render(request, 'carts/checkout.html', context)

    except ObjectDoesNotExist:
        messages.error(request, 'Cart not found. Please add items to your cart.')
        return redirect('carts:carts')
    
    
def apply_coupon(request,cart_id):

    cart = Cart.objects.get(user=request.user, id=cart_id)
    if  request.method=='POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon)

        if not coupon_obj.exists():
            messages.warning(request,'Invalid Coupon!!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    
        if cart.coupon:
            messages.warning(request,'Coupon Exists already..')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    
        if cart.get_cart_total < coupon_obj[0].minimum_amount:
            messages.warning(request,f'Amount should be greater than {coupon_obj[0].minimum_amount}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    
        if coupon_obj[0].is_expired:
            messages.warning(request,f'Coupon is expired')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    
        cart.coupon = coupon_obj[0]
        cart.save()
        messages.success(request,'Coupon applied..')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('carts:checkout')      

def remove_coupon(request,cart_id):          
    cart = Cart.objects.get(id=cart_id)
    cart.coupon=None
    cart.save()
    messages.success(request,'Coupon Removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def place_order(request):
    print("COD")
    if request.user.is_authenticated:
        if request.method == 'POST':
            selected_payment_method = request.POST.get('payment_method')
            selected_address_id = request.POST.get('shipping_address')

            try:
                selected_address = ShippingAddress.objects.get(id=selected_address_id)
            except ShippingAddress.DoesNotExist:
                messages.error(request, "Please select a valid shipping address before placing your order.")
                return redirect('carts:checkout')

            cart = Cart.objects.get(user=request.user, complete=False)
            cart_items = CartItem.objects.filter(order=cart)

            if not cart_items:
                messages.error(request, "Your cart is empty. Add items to your cart before placing an order.")
                return redirect('carts:carts')

            cart = Cart(
                user=request.user,
                shipping_address=selected_address,
                payment_method=selected_payment_method,  # Set the payment method as needed
            )
            
            cart.save()

            for cart_item in cart_items:
                cart_item.order = cart
                cart_item.delivery_status = 'PL'
                cart_item.save()

            cart.complete = True
            cart.save()

            messages.success(request, 'Your order has been placed successfully!')
            return redirect('carts:order_placed')

    return redirect('carts:checkout')



@login_required
def add_address(request):
    

    if request.method == 'POST':
        # Create a new address
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'User address added successfully.')
            return redirect('carts:checkout')
        
    else:
        address_form = AddressForm()

    return render(request, 'carts/add_address.html', {'address_form': address_form})

def razorpaycheck(request):
    try:
        cart = Cart.objects.filter(user=request.user, complete=False).latest('date_added')
        cart_items = CartItem.objects.filter(order=cart)
        total_price = 0

        for cart_item in cart_items:
                total_price += cart_item.get_total
                

        return JsonResponse ({
                'total_price' : total_price,
            })
    except Cart.DoesNotExist:
        return JsonResponse({'total_price': 0, 'error': 'Cart not found'})


def place_order_raz(request):
    if request.method == 'POST':
        selected_address_id = request.POST.get('selectedAddressId')
        # order_notes = request.POST.get('orderNotes')
        transaction_id = request.POST.get('transaction_id')
        
        

        try:
            selected_address = ShippingAddress.objects.get(id=selected_address_id)
        except ShippingAddress.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid shipping address'})


        order = Cart(
            user=request.user,
            payment_method='RAZ',
            shipping_address=selected_address,
            transaction_id=transaction_id
        )
          

        order.complete = True
        order.save()

        cart_items = CartItem.objects.filter(order__user=request.user, order__complete=False)
        for cart_item in cart_items:
            cart_item.order = order
            cart_item.delivery_status = 'PL'
            cart_item.save()
            
        cart_items.delete()

        return JsonResponse({'status': 'success', 'message': 'Your order has been placed successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def order_placed(request):
    return render(request, 'carts/order_placed.html')








# def place_order_raz(request):
#     print("Razorpay working")
#     if request.method == 'POST':
#         selected_address_id = request.POST.get('selectedAddressId')
      
#         transaction_id = request.POST.get('transaction_id')
        
        

#         try:
#             selected_address = ShippingAddress.objects.get(id=selected_address_id)
#         except ShippingAddress.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Invalid shipping address'})


#         # Create the order
#         order = Cart(
#             user=request.user,
#             payment_method='RAZ',
#             transaction_id=transaction_id,
#             shipping_address=selected_address,
           
#         )
        
#         print(order)
#         order.save()
       

#         # Mark the order as complete
#         order.complete = True
#         order.save()

#         # # Update order items (if needed)
#         # cart_items = CartItem.objects.filter(order__user=request.user, order__complete=True)
#         # for cart_item in cart_items:
#         #     cart_item.order = order
#         #     cart_item.delivery_status = 'PL'
#         #     cart_item.save()
            
#         #      # Empty the cart
#         # cart_items.delete()

#         return JsonResponse({'status': 'success', 'message': 'Your order has been placed successfully!'})

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
