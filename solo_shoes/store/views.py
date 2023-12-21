from django.utils import timezone
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect
from custom_admin_panel.models import Product
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem, Whishlist
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator

from store.models import Offer,OfferCategory


# Create your views here.
def shop(request, category=None):
    if category:
        products = Product.objects.filter(category__category_name__iexact=category, is_available=True)
        paginator = Paginator(products,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.filter(is_available=True)
        paginator = Paginator(products,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    
    for product in paged_products:
        now = timezone.now()
        
        product.offer = Offer.objects.filter(
        Q(product=product) & Q(date_start__lte=now, date_end__gt=now)).first()

        product.category.offer = OfferCategory.objects.filter(
        Q(category=product.category) & Q(date_start__lte=now, date_end__gt=now)).first()
        

        if product.offer and product.category.offer:
            discount_percentage = max(product.offer.discount_percentage, product.category.offer.discount_percentage)

            
        elif product.category.offer:
             
            discount_percentage = product.category.offer.discount_percentage

        elif product.offer:
            discount_percentage = product.offer.discount_percentage

        else:
            discount_percentage = 0

        if discount_percentage > 0:
            discount_factor = Decimal(discount_percentage) / Decimal(100)
            product.discounted_price = product.price - (product.price * discount_factor)
        else:
            product.discounted_price = None
    

    context = {
        'products': paged_products,
        # 'paged_products' : paged_products,
        'category': category,
    }
    return render(request, 'store/shop.html', context)


def search_by_price(request):
    default_min_price = 100.0
    default_max_price = 3000.0

    
    min_price_str = request.GET.get('min_price', str(default_min_price))
    max_price_str = request.GET.get('max_price', str(default_max_price))

    print(f"min_price_str: {min_price_str}, max_price_str: {max_price_str}")


    
    try:
        min_price = float(min_price_str)
        max_price = float(max_price_str)
    except ValueError:
        min_price, max_price = default_min_price, default_max_price
    
    print(f"min_price: {min_price}, max_price: {max_price}")


    
    filtered_products = Product.objects.filter(price__gte=min_price, price__lte=max_price)
    print(f"filtered_products: {filtered_products}")

    for product in filtered_products:
        now = timezone.now()
        
        product.offer = Offer.objects.filter(
        Q(product=product) & Q(date_start__lte=now, date_end__gt=now)).first()

        product.category.offer = OfferCategory.objects.filter(
        Q(category=product.category) & Q(date_start__lte=now, date_end__gt=now)).first()
        

        if product.offer and product.category.offer:
            discount_percentage = max(product.offer.discount_percentage, product.category.offer.discount_percentage)

            
        elif product.category.offer:
             
            discount_percentage = product.category.offer.discount_percentage

        elif product.offer:
            discount_percentage = product.offer.discount_percentage

        else:
            discount_percentage = 0

        if discount_percentage > 0:
            discount_factor = Decimal(discount_percentage) / Decimal(100)
            product.discounted_price = product.price - (product.price * discount_factor)
        else:
            product.discounted_price = None

    context = {
        'filtered_products': filtered_products,
    }

    return render(request, 'store/shop.html', context)

def product(request,product_id):
    product = get_object_or_404(Product, pk=product_id)
    category = product.category
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
    related_products = Product.objects.filter(category=category, is_available=True).exclude(pk=product.id)[:4]

    for related_product in related_products:
        now = timezone.now()
        
        related_product.offer = Offer.objects.filter(
        Q(product=related_product) & Q(date_start__lte=now, date_end__gt=now)).first()

        related_product.category.offer = OfferCategory.objects.filter(
        Q(category=related_product.category) & Q(date_start__lte=now, date_end__gt=now)).first()

        if related_product.offer and related_product.category.offer:
            if related_product.offer.discount_percentage > related_product.category.offer.discount_percentage:
                discount_percentage = Decimal(related_product.offer.discount_percentage) / Decimal(100)
                related_product.discounted_price = related_product.price - (related_product.price * discount_percentage)
            else:
                discount_percentage = Decimal(related_product.category.offer.discount_percentage) / Decimal(100)
                related_product.discounted_price = related_product.price - (related_product.price * discount_percentage)
        elif related_product.category.offer:
            discount_percentage = Decimal(related_product.category.offer.discount_percentage) / Decimal(100)
            related_product.discounted_price = related_product.price - (related_product.price * discount_percentage)
        elif related_product.offer:
            discount_percentage = Decimal(related_product.offer.discount_percentage) / Decimal(100)
            related_product.discounted_price = related_product.price - (related_product.price * discount_percentage)
        else:
            related_product.discounted_price = None
    context = {
        'product':product,
        'related_products':related_products,
        'product_id': product_id
    }
       
    
    return render(request,'store/product.html', context)

@login_required
def wishlist(request):
    current_user = request.user
    wishlist = Whishlist.objects.get(user=current_user)

    context = {
        'wishlist': wishlist,
    }
    

    return render(request, 'store/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    response_data = {}
    print(product_id)
    try:
            if not request.user.is_authenticated:
                raise Exception('User not authenticated')

            wishlist, created = Whishlist.objects.get_or_create(user=request.user)
            product = get_object_or_404(Product, id=product_id)
            

            wishlist.products.add(product)
            wishlist.save()
            print("XXXX",wishlist.products.all())

            response_data['success'] = True
            response_data['message'] = 'Item added to your wishlist'
    except Exception as e:
            response_data['success'] = False
            response_data['error'] = str(e)

    return JsonResponse(response_data)





@login_required
def remove_from_wishlist(request, product_id):
    wishlist = get_object_or_404(Whishlist, user=request.user)
    product = get_object_or_404(Product, id=product_id)

    wishlist.products.remove(product)
    wishlist.save()

    messages.success(request, 'Product removed from wishlist successfully.')

    return redirect('store:wishlist')

