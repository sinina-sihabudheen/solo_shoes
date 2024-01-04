from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
# from django.urls import reverse
from custom_admin_panel.models import Product
from carts.models import Cart, CartItem, ShoppingCart, Whishlist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from store.models import Offer, OfferCategory
from user_profile.models import ShippingAddress, Wallet
from django.contrib.auth.decorators import login_required
from user_profile.forms import AddressForm
from django.db import transaction 
from decimal import Decimal
from .models import Cart, CartItem, Coupon
from django.utils import timezone



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
    product = get_object_or_404(Product, id=product_id)
    current_user = request.user

    if current_user.is_authenticated:
        # Get all incomplete carts for the user
        carts = Cart.objects.filter(user=current_user, complete=False)

        if carts.exists():
            # Choose the first cart if there are multiple incomplete carts
            cart = carts.first()
        else:
            # Create a new cart if none exists
            cart = Cart.objects.create(user=current_user, complete=False)

        if not cart.shopping_cart:
            cart.shopping_cart, created = ShoppingCart.objects.get_or_create(session_key=request.session.session_key)

        cart.save()
        
        # Check if the product is already in the cart
        existing_cart_item = CartItem.objects.filter(order=cart, product=product).first()

        if existing_cart_item:
            # If the product is already in the cart, increase the quantity
            existing_cart_item.quantity += 1
            existing_cart_item.save()
        else:
            # If the product is not in the cart, create a new CartItem
            cart_item = CartItem.objects.create(order=cart, product=product, quantity=1)
            
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

    if request.method == 'POST':
        current_user = request.user

        if current_user.is_authenticated:
            carts = Cart.objects.filter(user=current_user, complete=False)

            if carts.exists():
                cart = carts.first()

                # Use filter() instead of get()
                cart_items = CartItem.objects.filter(order=cart, product=product)

                if cart_items.exists():
                    # Choose to delete all items or just one (use [0] for one)
                    cart_items.delete()

                    product.stock += 1
                    product.save()

                    messages.success(request, f"{product.product_name} removed from the cart.")
                else:
                    messages.error(request, f"{product.product_name} not found in the cart.")
        
    return redirect('carts:carts')



def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        
        # Use filter to get a queryset and first() to retrieve the first object
        carts = Cart.objects.filter(user=request.user, complete=False)
        cart = carts.first()

        if not cart:
            messages.error(request, "Cart not found.")
            return redirect('carts:carts')

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
            carts = Cart.objects.filter(user=request.user, complete=False)
            if carts.exists():
                cart = carts.first()
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

                    # Store the product name at the time of order placement
                    cart_item.product_name_at_order = cart_item.product.product_name
                    cart_item.save()

                    # Update total and quantity
                    if cart_item.discounted_price is not None:
                        total += cart_item.discounted_price * cart_item.quantity
                    else:
                        total += cart_item.product.price * cart_item.quantity
                    
                    quantity += cart_item.quantity
            else:
                cart_items = []

    except ObjectDoesNotExist:
        cart_items = []

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'cart': cart if 'cart' in locals() else None,
    }

    return render(request, 'carts/cart.html', context)


def checkout(request):
    try:
        cart = Cart.objects.filter(user=request.user, complete=False).first()
        if cart:
            cart_items = CartItem.objects.filter(order=cart)
            user_address = ShippingAddress.objects.filter(user=request.user, status=True).first()
            cart.coupon = None
            cart.save()
            wallet = Wallet.objects.get(user=request.user)

            # Calculate total and quantity
            total = 0
            quantity = 0
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity

           
            cart.save()

            user_addresses = ShippingAddress.objects.filter(user=request.user)

            context = {
                'cart': cart,
                'user_address': user_address,
                'user_addresses': user_addresses,
                'cart_items': cart_items,
                'total': total,
                'quantity': quantity,
                'wallet': wallet,
            }

            return render(request, 'carts/checkout.html', context)
        else:
            messages.error(request, 'Cart not found. Please add items to your cart.')
            return redirect('carts:carts')

    except ObjectDoesNotExist:
        messages.error(request, 'Cart not found. Please add items to your cart.')
        return redirect('carts:carts')

    
def apply_coupon(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)
    cart = Cart.objects.get(user=request.user, id=cart_id)
    
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon')
        
        try:
            coupon = Coupon.objects.get(coupon_code__icontains=coupon_code)
            
            if coupon.valid_till < timezone.now():
                messages.error(request, 'Coupon has expired.', extra_tags='danger')
            elif cart.get_cart_total < coupon.minimum_amount:
                messages.error(request, f'Amount should be greater than {coupon.minimum_amount}', extra_tags='danger')
            elif not coupon.is_user_eligible(request.user):
                messages.error(request, 'You have already used this coupon.', extra_tags='danger')
            elif coupon.mark_as_used(request.user):
                messages.error(request, 'You have already used this coupon.', extra_tags='danger')
            elif coupon.status == False:
                messages.error(request, 'This coupon does not exist now..', extra_tags='danger')
            elif cart.coupon:
                messages.error(request, 'Coupon already applied.', extra_tags='danger')
            else:
                cart.coupon = coupon
                cart.save()
                
                messages.success(request, 'Coupon successfully applied.', extra_tags='success')
            
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code. Please try again.', extra_tags='danger')

    cart_items = CartItem.objects.filter(order=cart)  # Change 'cart' to 'order'
    user_address = ShippingAddress.objects.filter(user=request.user, status=True).first()
    cart.save()
    wallet = Wallet.objects.get(user=request.user)

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
        'wallet': wallet,
    }

    return render(request, 'carts/checkout.html', context)



def remove_coupon(request,cart_id):          
    cart = Cart.objects.get(id=cart_id)
    cart.coupon=None
    cart.save()
    messages.success(request,'Coupon Removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def place_order(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            selected_payment_method = request.POST.get('payment')
    
            selected_address_id = request.POST.get('shipping_address')

            try:
                selected_address = ShippingAddress.objects.get(id=selected_address_id)
            except ShippingAddress.DoesNotExist:
                messages.error(request, "Please select a valid shipping address before placing your order.")
                return redirect('carts:checkout')

            carts = Cart.objects.filter(user=request.user, complete=False)

            if not carts.exists():
                messages.error(request, "Your cart is empty. Add items to your cart before placing an order.")
                return redirect('carts:carts')
            cart = carts.first()
            cart_items = CartItem.objects.filter(order=cart)

            if not cart_items:
                messages.error(request, "Your cart is empty. Add items to your cart before placing an order.")
                return redirect('carts:carts')

            # Save the order with the selected shipping address
            with transaction.atomic():
                cart = Cart.objects.select_for_update().filter(user=request.user, complete=False).first()
                cart.user = request.user
                cart.full_name = selected_address.full_name
                cart.address_lines = selected_address.address_lines
                cart.city = selected_address.city
                cart.state = selected_address.state
                cart.pin_code = selected_address.pin_code
                cart.country = selected_address.country
                cart.mobile = selected_address.mobile
                cart.cart_total_at_order = cart.get_cart_total
                               
                cart.payment_method = selected_payment_method
                print(cart.payment_method)
                cart.save()
                if cart.coupon:
                    cart.coupon = cart.coupon
                    cart.coupon.mark_as_used(request.user)

                cart.save()

                # Store the user's current shipping address for the order
                cart.shipping_address_for_orders = selected_address
                cart.save()

                if selected_payment_method == 'wal':
                    total_amount = sum(cart_item.get_total for cart_item in cart_items)
                    user_wallet = Wallet.objects.get(user=request.user)
                    user_wallet.balance -= total_amount
                    user_wallet.save()

                for cart_item in cart_items:
                    
                    cart_item.order = cart
                    cart_item.delivery_status = 'PL'
                    cart_item.product_name_at_order = cart_item.product.product_name
                    cart_item.product_description_at_order = cart_item.product.description
                    cart_item.product_price_at_order = cart_item.product.price
                    cart_item.product_stock_at_order = cart_item.product.stock
                    
                    cart_item.save()
                
                cart.cart_total_at_order = cart.get_cart_total_at_order
                cart.cart_items_total_at_order = cart.get_cart_items
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

@transaction.atomic
def razorpaycheck(request):
    try:
        cart = Cart.objects.get(user=request.user, complete=False)
        cart_items = CartItem.objects.filter(order=cart)
        total_price =cart.get_cart_total
        
        
        return JsonResponse ({
                'total_price' : total_price,
            })
    except Cart.DoesNotExist:
        return JsonResponse({'total_price': 0, 'error': 'Cart not found'})


def place_order_raz(request):
    if request.method == 'POST':
        selected_address_id = request.POST.get('selectedAddressId')
        transaction_id = request.POST.get('transaction_id')       

        try:
            selected_address = ShippingAddress.objects.get(id=selected_address_id)
        except ShippingAddress.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid shipping address'})


        order = Cart(
            user=request.user,
            payment_method='RAZ',
            full_name = selected_address.full_name,
            address_lines = selected_address.address_lines,
            city = selected_address.city,
            state = selected_address.state,
            pin_code = selected_address.pin_code,
            country = selected_address.country,
            mobile = selected_address.mobile,
            # cart_total_at_order = cart.get_cart_total,
            transaction_id=transaction_id
        )
          
        cart = Cart.objects.select_for_update().get(user=request.user, complete=False)
        if cart.coupon:
            order.coupon = cart.coupon
            order.coupon.mark_as_used(request.user)
        order.complete = True
        order.save()

        cart_items = CartItem.objects.filter(order__user=request.user, order__complete=False)
        for cart_item in cart_items:
            cart_item.order = order
            cart_item.delivery_status = 'PL'
            cart_item.product_name_at_order = cart_item.product.product_name
            cart_item.product_description_at_order = cart_item.product.description
            cart_item.product_price_at_order = cart_item.product.price
            cart_item.product_stock_at_order = cart_item.product.stock
            cart_item.save()
        
        if order.coupon:
                    order.coupon = order.coupon
                    order.coupon.mark_as_used(request.user)
        order.cart_total_at_order = order.get_cart_total
        order.cart_items_total_at_order = order.get_cart_items
        order.complete = True
        order.save()   
        cart_items.delete()

        return JsonResponse({'status': 'success', 'message': 'Your order has been placed successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def order_placed(request):
    return render(request, 'carts/order_placed.html')






