
from django.db.models import Prefetch
from django.db.models import Q, F, Sum
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from django.utils import timezone
from carts.models import Cart, CartItem, Coupon
# from custom_admin_panel.helpers import render_to_pdf
from store.models import Offer, OfferCategory
from .models import Category, Product, ProductImage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.utils import timezone
from .forms import CartItemForm, ProductForm, CategoryForm, ProductImageFormSet
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
# from django.template.loader import get_template
# from xhtml2pdf import pisa
from django.views.decorators.http import require_GET
from django.db.models.functions import TruncWeek, TruncMonth, TruncDay
from .forms import OfferForm,OfferCategoryForm, CouponForm
from django.views.decorators.http import require_POST


# Create your views here.


def admin_login(request):
   
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        admin=authenticate(username=username,password=password)
        if admin and admin.is_superuser:
            login(request, admin)
            request.session['username'] = admin.username 
            return redirect('custom_admin_panel:dashboard')
        else:
            messages.error(request,"Bad Credentials.! ")
            return redirect('custom_admin_panel:adminlogin')


    return render(request,'custom_admin_panel/adminlogin.html')


@login_required(login_url='custom_admin_panel:adminlogin')
def dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        user = User.objects.all()
        query = request.GET.get('text')

        if query:
            emp = emp.filter(Q(first_name_icontains=query) | Q(emailicontains=query) | Q(username_icontains=query))
        
        all_orders = Cart.objects.all()

        all_orders_filter = Cart.objects.filter(
    (
        Q(payment_method='COD') & Q(cartitem__delivery_status='D')
    ) | (
        Q(payment_method__in=['RAZ', 'WAL']) & ~Q(cartitem__delivery_status__in=['C', 'RT'])
    )
)
        
        
        order_delivered = CartItem.objects.filter(
    Q(order__payment_method='COD') | Q(order__payment_method='RAZ') | Q(order__payment_method='WAL'),
    ~Q(delivery_status__in=['C', 'RT'])
)
        
        all_order_items = CartItem.objects.filter(~Q(delivery_status='C') or ~Q(delivery_status='RT'))
        

        
        filter_type = request.GET.get('filter_type', 'all')  

    
        if filter_type == 'day':
            start_date = datetime.now() - timedelta(days=1)
        elif filter_type == 'week':
            start_date = datetime.now() - timedelta(weeks=1)
        elif filter_type == 'month':
            start_date = datetime.now() - timedelta(weeks=4)  
        elif filter_type == 'year':
            start_date = datetime.now() - timedelta(weeks=52)  
        else:
            start_date = None  
        
        if start_date:
            all_orders = all_orders.filter(date_added__gte=start_date)
        products = Product.objects.all()
        
        total_revenue = sum(order.get_total for order in order_delivered)
        total_sales = all_orders_filter.count()
        total_stock = sum(product.stock for product in products)
                     
        cod_orders = all_orders.filter(payment_method='COD')
        raz_orders = all_orders.filter(payment_method='RAZ')
        wallet_orders = all_orders.filter(payment_method='WAL')

        cod_count = cod_orders.count()    
        raz_count = raz_orders.count()
        wallet_count = wallet_orders.count()


        cod_total = sum(order.get_cart_total_at_order for order in cod_orders)
        raz_total = sum(order.get_cart_total_at_order for order in raz_orders)
        wallet_total = sum(order.get_cart_total_at_order for order in wallet_orders)

        returned_amount_cod = sum(item.get_total_at_order for item in all_order_items.filter(order__payment_method='COD', delivery_status='RT'))
        cancelled_amount_cod = sum(item.get_total_at_order for item in all_order_items.filter(order__payment_method='COD', delivery_status='CN'))

        returned_amount_raz = sum(item.get_total_at_order for item in all_order_items.filter(order__payment_method='RAZ',delivery_status='RT'))
        cancelled_amount_raz = sum(item.get_total_at_order for item in all_order_items.filter(order__payment_method='RAZ',delivery_status='CN'))

        returned_amount_wallet = sum(item.get_total_at_order for item in all_order_items.filter(order__payment_method='WAL',delivery_status='RT'))
        cancelled_amount_wallet = sum(item.get_total_at_order for item in all_order_items.filter(order__payment_method='WAL',delivery_status='CN'))
                

        context = {
            'user':user,
            'total_revenue': total_revenue,
            'total_sales' : total_sales,        
            'all_orders':all_orders,
            'all_order_items':all_order_items,
            'cod_count': cod_count,            
            'cod_total': cod_total,  
            'raz_count': raz_count,
            'raz_total': raz_total,  
            'wallet_count': wallet_count,
            'wallet_total': wallet_total,  
            'filter_type': filter_type,  
            'order_delivered': order_delivered,
            'total_stock' : total_stock,
            'returned_amount_cod': returned_amount_cod,
            'returned_amount_raz': returned_amount_raz,
            'returned_amount_wallet': returned_amount_wallet,
            'cancelled_amount_cod': cancelled_amount_cod,
            'cancelled_amount_raz': cancelled_amount_raz,
            'cancelled_amount_wallet': cancelled_amount_wallet,
        }

        return render(request,'custom_admin_panel/dashboard.html',context)
    return redirect('custom_admin_panel:adminlogin')



def block_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    return redirect('custom_admin_panel:user_management')

def unblock_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    return redirect('custom_admin_panel:user_management')



@login_required(login_url='custom_admin_panel:adminlogin')
def user_management(request):
    search_query = request.GET.get('key')
    cus = User.objects.all()
    
    if search_query:
        cus = cus.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query))
    context = {
        'cus': cus,
        'search_query': search_query,
    }
    return render(request, 'custom_admin_panel/user_list.html', context)


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_panel:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'custom_admin_panel/category_form.html', {'form': form})

def edit_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_panel:category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
            'form': form,
            'category': category

    }
    
    return render(request, 'custom_admin_panel/category_form.html', context)

def block_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.is_active = False
    category.save()
    return redirect('custom_admin_panel:category_list')

def unblock_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.is_active = True
    category.save()
    return redirect('custom_admin_panel:category_list')

@login_required(login_url='custom_admin_panel:adminlogin')
def category_list(request):
    query = request.GET.get('q')
    categories = Category.objects.all()
    form = CategoryForm()

    if query:
        categories = categories.filter(Q(category_name__icontains=query))
    
    for category in categories:
        # Fetch related offers for each category
        category.offers = OfferCategory.objects.filter(category=category)

        

    context = {
            'categories': categories, 
            'query': query,
            'form' : form,

    }

    return render(request, 'custom_admin_panel/category_list.html', context)

@login_required(login_url='custom_admin_panel:adminlogin')
def category_management(request):
    search_query = request.GET.get('q')
    categories = Category.objects.all()
    
    if search_query:
        categories = categories.filter(category_name__icontains=search_query)
    
    # debugging print statements
    print(f"Search query: {search_query}")
    print(f"Filtered users: {categories}")

    context = {
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'custom_admin_panel/category_list.html', context)


@login_required(login_url='custom_admin_panel:adminlogin')
def product_list(request):
    products = Product.objects.all()

    for product in products:
        product.offer = Offer.objects.filter(product=product).first()
        
        product.category.offer = OfferCategory.objects.filter(category=product.category).first()
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

    return render(request, 'custom_admin_panel/product_list.html', context)


def block_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    product.is_available = False
    product.save()
    return redirect('custom_admin_panel:product_list')

def unblock_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    product.is_available = True
    product.save()
    return redirect('custom_admin_panel:product_list')




def add_product(request):
    
    if request.method == 'POST':
        form = ProductForm(request.POST or None)
        formset = ProductImageFormSet(request.POST or None, request.FILES or None)

        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            return redirect('custom_admin_panel:product_list')
    else:
        form = ProductForm()
        formset = ProductImageFormSet(instance=Product())

    return render(request, 'custom_admin_panel/product_form.html', {'form': form, 'formset': formset})

def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = ProductForm(instance=product)
    
    # Check if the current product has any associated images
    formset = ProductImageFormSet(instance=product) if product.productimage_set.exists() else ProductImageFormSet()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('custom_admin_panel:product_list')

    return render(request, 'custom_admin_panel/product_form.html', {'form': form, 'formset': formset, 'product': product})

@login_required(login_url='custom_admin_panel:adminlogin')
def product_management(request):
    search_query = request.GET.get('key')
    products = Product.objects.all()
    
    if search_query:
        products = products.filter(product_name__icontains=search_query)
    
    # debugging print statements
    print(f"Search query: {search_query}")
    print(f"Filtered users: {products}")

    context = {
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'custom_admin_panel/product_list.html', context)

#Order Management...
@login_required(login_url='custom_admin_panel:adminlogin')
def order(request):
       
    
    orders_with_items = Cart.objects.filter(complete=True).all()

    context = {
        'orders_with_items': orders_with_items,
    }
    return render(request, 'custom_admin_panel/order_list.html', context)

@login_required(login_url='custom_admin_panel:adminlogin')
def order_details(request, order_item_id):
    order = get_object_or_404(Cart, id=order_item_id, complete=True)
    order_items = order.cartitem_set.all()
    orders_with_items = Cart.objects.filter(complete=True).prefetch_related(
        Prefetch('cartitem_set', queryset=CartItem.objects.select_related('product'))
    ).all()  

    context = {
        'order': order,
        'order_items': order_items,
        'orders_with_items': orders_with_items,
    }

    return render(request, 'custom_admin_panel/order_details.html', context)

@login_required(login_url='custom_admin_panel:adminlogin')
def order_edit(request, order_item_id):
    
    order_item = get_object_or_404(CartItem, id=order_item_id)

    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_panel:order')
    else:
        form = CartItemForm(instance=order_item)

    context = {
        'form': form,
        'order_item': order_item,
    }

    return render(request, 'custom_admin_panel/order_form.html', context)

@login_required(login_url='custom_admin_panel:adminlogin')
def cancel_order(request, order_item_id):
    order = get_object_or_404(CartItem, id=order_item_id)
    order.delivery_status = 'CN'
    order.save() 
    messages.success(request, 'Your order is successfully cancelled... ')
    return redirect('custom_admin_panel:order')

@login_required(login_url='custom_admin_panel:adminlogin')
def manage_offers_view(request):
    category_offers = OfferCategory.objects.all()
    product_offers = Offer.objects.all()

    context = {
        'category_offers' : category_offers,
        'product_offers' : product_offers,
    }

    return render(request, 'custom_admin_panel/offer.html', context)

@login_required(login_url='custom_admin_panel:adminlogin')
def category_off_add(request):
    if request.method == 'POST':
        form = OfferCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            offer_category = form.save(commit=False)            

            now = datetime.now(timezone.get_current_timezone())
            if offer_category.date_start <= now < offer_category.date_end:
                offer_category.active = True
            else:
                offer_category.active = False

            print("Active:", offer_category.active)

            offer_category.save()

            return redirect('custom_admin_panel:offer')
    else:
        form = OfferCategoryForm()

    return render(request, 'custom_admin_panel/category_offer.html', {'form': form})



@login_required(login_url='custom_admin_panel:adminlogin')
def category_off_edit(request, offer_id):
    offer = get_object_or_404(OfferCategory, pk=offer_id)

    if request.method == 'POST':
        form = OfferCategoryForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            offer_category = form.save(commit=False)
            now = timezone.now()
            if offer_category.date_start <= now < offer_category.date_end:
                offer_category.active = True
            else:
                offer_category.active = False

            offer_category.save()

            return redirect('custom_admin_panel:offer')
    else:
        form = OfferCategoryForm(instance=offer)

    context = {
        'form': form,
        'offer': offer,
    }

    return render(request, 'custom_admin_panel/category_offer.html', context)

@login_required(login_url='custom_admin_panel:adminlogin')
def product_off_add(request):
    if request.method == 'POST':
        form = OfferForm(request.POST or None)

        if form.is_valid():
            offer = form.save(commit=False)

            now = timezone.now()
            if offer.date_start <= now < offer.date_end:
                offer.active = True
            else:
                offer.active = False

            offer.save()
            return redirect('custom_admin_panel:offer')
    else:
        form = OfferForm()

    return render(request, 'custom_admin_panel/product_offer.html', {'form': form})

@login_required(login_url='custom_admin_panel:adminlogin')
def product_off_edit(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)
    form = OfferForm(instance=offer)

    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES, instance=offer)

        if form.is_valid():
            offer = form.save(commit=False)

            now = timezone.now()
            
            if offer.date_start <= now < offer.date_end:
                offer.active = True
            else:
                offer.active = False
            form.save()
            return redirect('custom_admin_panel:offer')
    
    context = {
        'form': form,
        'offer': offer,
    }

    return render(request, 'custom_admin_panel/product_offer.html', context)

# @login_required(login_url='custom_admin_panel:adminlogin')
# def sales_report(request):
#     delivered_order_items = CartItem.objects.filter(delivery_status='D' or Q(order__payment_method='RAZ' or 'WAL'))
#     # delivered_order_items = CartItem.objects.filter(order__delivery_status='D')

#     most_sold_products = (
#         delivered_order_items.values('product_price_at_order')
#         .annotate(total_sold=Sum('quantity'))
#         .order_by('-total_sold')[:6]
#     )    
#     return render(request,'custom_admin_panel/sales_report.html', { 'most_sold_products':most_sold_products })
@login_required(login_url='custom_admin_panel:adminlogin')
def sales_report(request):
    orders_with_items = Cart.objects.filter(complete=True).all()

    context = {
        'orders_with_items': orders_with_items,
    }
 
    return render(request,'custom_admin_panel/sales_report.html', context)

@require_GET
def get_sales_data(request, period):
    
    if period == 'week':
        start_date = timezone.now().date() - timezone.timedelta(days=6)
        order_items = CartItem.objects.filter(order__date_added__gte=start_date)
        data = (
            order_items.annotate(day=TruncDay('order__date_added'))
            .values('day')
            .annotate(total=Sum(F('quantity') * F('product_price_at_order')))
            .order_by('day')
        )
        labels = [item['day'].strftime('%A') for item in data]
        
    elif period == 'month':
        print("Entering into the month")
        start_date = timezone.now().date() - timezone.timedelta(days=30)
        order_items = CartItem.objects.filter(order__date_added__gte=start_date)
        data = (
        order_items.annotate(day=TruncDay('order__date_added'))
        .values('day')
        .annotate(total=Sum(F('quantity') * F('product_price_at_order')))
        .order_by('day')
    )
        labels = [item['day'].strftime('%Y-%m-%d') for item in data]
    # Example: Yearly sales
    elif period == 'year':
        print("Entering into the year")
        start_date = timezone.now().date() - timezone.timedelta(days=365)
        order_items = CartItem.objects.filter(order__date_added__gte=start_date)
        data = (
            order_items.annotate(month=TruncMonth('order__date_added'))
            .values('month')
            .annotate(total=Sum(F('quantity') * F('product_price_at_order')))
            .order_by('month')
        )
        labels = [f"{item['month'].strftime('%B')}" for item in data]
    else:
        return JsonResponse({'error': 'Invalid period'})

    
    
    sales_data = [item['total'] for item in data]

    return JsonResponse({'labels': labels, 'data': sales_data})


@login_required(login_url='custom_admin_panel:adminlogin')
@require_POST
def sales_details(request):
    start_date_str = request.POST.get('start_date')
    end_date_str = request.POST.get('end_date')

    if not start_date_str or not end_date_str:
        return HttpResponseBadRequest("Invalid date parameters")
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)

    start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
    end_date = timezone.make_aware(end_date, timezone.get_current_timezone())

    
    order_items = CartItem.objects.filter(
    Q(order__date_added__range=(start_date, end_date)) &
    Q(order__isnull=False) &
    Q(delivery_status='D') |
    Q(
        Q(order__payment_method__in=['WAL', 'RAZ']) &
        ~Q(delivery_status__in=['RT', 'CN'])
    )
)

    product_quantities = order_items.values('product_price_at_order').annotate(total_quantity=Sum('quantity'))

    context = {
        'order_items': order_items,
        'product_quantities': product_quantities,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }

    return render(request, 'custom_admin_panel/salespdf.html', context)

def coupon_list(request):
    coupons= Coupon.objects.all()
    context={
        'coupons':coupons
        }
    return render(request,'custom_admin_panel/coupon.html',context)

def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_panel:coupon_list')
    else:
        form = CouponForm()
    
    return render(request, 'custom_admin_panel/coupon_form.html', {'form': form})

def edit_coupon(request,coupon_id):

    coupon = get_object_or_404(Coupon, pk=coupon_id)

    if request.method == 'POST':
            form = CouponForm(request.POST, request.FILES, instance=coupon)
            if form.is_valid():
                form.save()
                return redirect('custom_admin_panel:coupon_list')
    else:
            form = CouponForm(instance=coupon)
        
    context = {
                'form': form,
                'coupon': coupon,

        }
        
    return render(request, 'custom_admin_panel/coupon_form.html', context)

def toggle_coupon_status(request, coupon_id):
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    
    # Toggle the status
    new_status = not coupon.status
    coupon.status = new_status
    coupon.save()
    
    return redirect('custom_admin_panel:coupon_list')
def block_coupon(request, coupon_id):
    return toggle_coupon_status(request, coupon_id, False)

def unblock_coupon(request, coupon_id):
    return toggle_coupon_status(request, coupon_id, True)

@never_cache
def admin_logout(request):
    if request.user.is_authenticated and request.user.is_superuser:
        logout(request)
    return redirect('custom_admin_panel:adminlogin')


