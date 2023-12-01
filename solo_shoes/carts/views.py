from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from custom_admin_panel.models import Product
from carts.models import Cart, CartItem, ShoppingCart, Whishlist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from store.models import Offer, OfferCategory
from user_profile.models import ShippingAddress
from django.db import transaction
from user_profile.models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from user_profile.forms import AddressForm
from django.db import transaction 



def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        request.session.save()
        cart = request.session.session_key
        shopping_cart, created = ShoppingCart.objects.get_or_create(session_key=cart)
        
        # Assuming you want to associate the shopping cart with the user's cart if the user is authenticated
        if request.user.is_authenticated:
            user_cart, _ = Cart.objects.get_or_create(user=request.user, shopping_cart=shopping_cart)
        
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        # Handle the case where the product with the given ID doesn't exist
        messages.error(request, "Product not found.")
        return redirect('carts:carts')
    
    current_user = request.user
    
    if current_user.is_authenticated:
        # If the user is authenticated, associate the Cart with the user's shopping cart
        cart, _ = Cart.objects.get_or_create(user=current_user)
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

    # Save the changes to the CartItem
        cart_item.save()

    # Update the stock of the product and save it
        product.stock -= 1
        product.save()
    #Remove the product from whishlist    
    try:
         wishlist = Whishlist.objects.get(user=request.user)
    except ObjectDoesNotExist:
    # Wishlist doesn't exist, create a new one
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
        cart, _ = Cart.objects.get_or_create(user=current_user)
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
        quantity = request.POST.get('quantity')
        action = request.POST.get('action')
        product = Product.objects.get(id=product_id)

        cart_item = get_object_or_404(CartItem, product__id=product_id, order__user=request.user.id)

        try:
            if quantity is not None:
                quantity = int(quantity)
                if action == 'increment':
                    if product.stock>0:
                        cart_item.quantity += 1
                        product.stock-=1
                        product.save()
                elif action == 'decrement':
                    cart_item.quantity -= 1
                    product.stock+=1
                    product.save()
                    if cart_item.quantity <= 0:
                        cart_item.delete()
                cart_item.save()
                messages.success(request, 'Cart updated successfully.')
            else:
                messages.warning(request, 'Quantity not provided.')
        except ValueError:
            messages.error(request, 'Invalid quantity value.')

    return redirect('carts:carts')



from decimal import Decimal

def carts(request, total=0, quantity=0):
    try:
        if request.user.is_authenticated:
            cart_instance = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(order=cart_instance)

            for cart_item in cart_items:
                cart_item.offer = Offer.objects.filter(product=cart_item.product).first()
                product_category = cart_item.product.category  
                cart_item.product.category.offer = OfferCategory.objects.filter(category=product_category).first()
                
                if cart_item.offer and cart_item.product.category.offer:
                    discount_percentage = max(cart_item.offer.discount_percentage, cart_item.product.category.offer.discount_percentage)
                elif cart_item.product.category.offer:
                    discount_percentage = cart_item.product.category.offer.discount_percentage
                elif cart_item.offer:
                    discount_percentage = cart_item.offer.discount_percentage
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
    }

    return render(request, 'carts/cart.html', context)







def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(order=cart)
        user_address = ShippingAddress.objects.filter(user=request.user, status=True).first()

        # Calculate total and quantity
        total = 0
        quantity = 0
        for cart_item in cart_items:
                cart_item.offer = Offer.objects.filter(product=cart_item.product).first()
                product_category = cart_item.product.category  
                cart_item.product.category.offer = OfferCategory.objects.filter(category=product_category).first()
                
                if cart_item.offer and cart_item.product.category.offer:
                    discount_percentage = max(cart_item.offer.discount_percentage, cart_item.product.category.offer.discount_percentage)
                elif cart_item.product.category.offer:
                    discount_percentage = cart_item.product.category.offer.discount_percentage
                elif cart_item.offer:
                    discount_percentage = cart_item.offer.discount_percentage
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

        if request.method == 'POST':
            # Check if the form is for a new address
            if 'billing_first_name' in request.POST:
                # Process the new address form
                address_form = AddressForm(request.POST)
                if address_form.is_valid():
                    with transaction.atomic():
                        # Create a new address
                        new_address = address_form.save(commit=False)
                        new_address.user = request.user
                        new_address.save()
                        messages.success(request, 'New address added successfully.')

                        # Redirect to the checkout page again
                        return redirect('carts:checkout')
                else:
                    messages.error(request, 'Error adding the address. Please check the form.')
            else:
                # Process the checkout form for placing the order
                with transaction.atomic():
                    # Create a new order
                    order = Order.objects.create(
                        customer=request.user,
                        complete=False,
                        payment_method='COD',  # Set the payment method as needed
                        shipping_address=user_address,
                        # order_notes=request.POST.get('order_notes', ''),  
                    )

                    # Associate each cart item with the order
                    for cart_item in cart_items:
                        OrderItem.objects.create(
                            product=cart_item.product,
                            order=order,
                            quantity=cart_item.quantity,
                            delivery_status='PL',  
                        )

                    # Clear the cart
                    cart_items.delete()

                    messages.success(request, 'Order placed successfully!')
                    return redirect('carts:order_placed')

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


def place_order(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            selected_payment_method = request.POST.get('payment_method')
            selected_address_id = request.POST.get('selected_address')
            
            try:
                selected_address = ShippingAddress.objects.get(id=selected_address_id)
            except ShippingAddress.DoesNotExist:
                messages.error(request, "Please select a valid shipping address before placing your order.")
                return redirect('carts:checkout') 
            
            cart_items = OrderItem.objects.filter(order_customer=request.user, order_complete=False)
            if not cart_items:
                messages.error(request, "Your cart is empty. Add items to your cart before placing an order.")
                return redirect('carts:carts')
            
                       
            order = Order(
                customer=request.user, 
                shipping_address=selected_address,
                
            )
            
           
                       
            order.save()
            
            if selected_payment_method == 'cod':
                order.payment_method='COD'        
                          
                order.complete = True
                order.save()
            
           
                for cart_item in cart_items:
                    cart_item.order = order 
                    cart_item.delivery_status = 'PL'
                    cart_item.save()
           
                messages.success(request, 'Your order has been placed successfully!')                
                return redirect('carts:order_placed')
            else:
                messages.warning(request, 'Online payment is not supported in this example. Please choose COD.')

    return render(request, "carts/checkout.html")

@login_required
def add_address(request):
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
            return redirect('carts:checkout')
        
    else:
        address_form = AddressForm()

    return render(request, 'carts/checkout.html', {'address_form': address_form, 'user_addresses': user_addresses})


def order_placed(request):
    return render(request, 'carts/order_placed.html')

