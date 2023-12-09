from datetime import datetime, timedelta
from django.db.models import Prefetch
from django.db.models import Q, F, Sum
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from datetime import datetime, timezone
from django.utils import timezone
from carts.models import Cart, CartItem
# from custom_admin_panel.helpers import render_to_pdf
from store.models import Offer, OfferCategory
from .models import Category, Product, ProductImage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

from .forms import ProductForm, CategoryForm, ProductImageFormSet
from django.http import HttpResponse, JsonResponse
# from django.template.loader import get_template
# from xhtml2pdf import pisa
from django.views.decorators.http import require_GET
from django.db.models.functions import TruncWeek, TruncMonth, TruncDay


from user_profile.forms import OrderForm
from .forms import OfferForm,OfferCategoryForm


# from django.urls import reverse_lazy




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


# @login_required
# def dashboard(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#         user = User.objects.all()
#         query = request.GET.get('text')

#         if query:
#             emp = emp.filter(Q(first_name_icontains=query) | Q(emailicontains=query) | Q(username_icontains=query))



#         context = {
#             'user':user,
            
#         }

#         return render(request,'custom_admin_panel/dashboard.html',context)
#     return redirect('custom_admin_panel:adminlogin')

@login_required(login_url='custom_admin_panel:adminlogin')
def dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        user = User.objects.all()
        query = request.GET.get('text')

        if query:
            emp = emp.filter(Q(first_name_icontains=query) | Q(emailicontains=query) | Q(username_icontains=query))
        
        all_orders = Cart.objects.all()

        order_delivered = CartItem.objects.filter(delivery_status='D')
        
        all_order_items = CartItem.objects.all()
        

        
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

        
        total_revenue = sum(order.get_cart_total for order in all_orders)
        total_sales = sum(order.get_cart_items for order in all_orders)
                     
        cod_orders = all_orders.filter(payment_method='COD')
        cod_count = cod_orders.count()    
        cod_total = sum(order.get_cart_total for order in cod_orders)
        products = Product.objects.all() 
        total_stock = sum(product.stock for product in products)

        context = {
            'user':user,
            'total_revenue': total_revenue,
            'total_sales' : total_sales,        
            'all_orders':all_orders,
            'all_order_items':all_order_items,
            'cod_count': cod_count,            
            'cod_total': cod_total,        
            'filter_type': filter_type,  
            'order_delivered': order_delivered,
            'total_stock' : total_stock,
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
    
    # debugging print statements
    print(f"Search query: {search_query}")
    print(f"Filtered users: {cus}")

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



#Order Management...
@login_required(login_url='custom_admin_panel:adminlogin')
def order(request):
    target_payment_method = 'COD'  # Change this to the desired payment method

    # Fetch orders with the specified payment method along with their related items
    orders_with_items = Cart.objects.filter(payment_method=target_payment_method).prefetch_related(
        Prefetch('cartitem_set', queryset=CartItem.objects.select_related('product'))
    ).all()

    context = {
        'orders_with_items': orders_with_items,
    }
    return render(request, 'custom_admin_panel/order_list.html', context)

def order_edit(request, order_item_id):
    
    order_item = get_object_or_404(CartItem, id=order_item_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_panel:order')
    else:
        form = OrderForm(instance=order_item)

    context = {
        'form': form,
        'order_item': order_item,
    }

    return render(request, 'custom_admin_panel/order_form.html', context)

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

def category_off_add(request):
    if request.method == 'POST':
        form = OfferCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            offer_category = form.save(commit=False)
            

            now = datetime.now(timezone.get_current_timezone())
            print("Now:", now)
            print("Start Date:", offer_category.date_start)
            print("End Date:", offer_category.date_end)
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

@login_required(login_url='custom_admin_panel:adminlogin')
def sales_report(request):
    delivered_order_items = CartItem.objects.filter(delivery_status='D')
    print(delivered_order_items)
    most_sold_products = (
        delivered_order_items.values('product__product_name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:6]
    )
    print('MOST SOLDLllllll',most_sold_products)
    return render(request,'custom_admin_panel/sales_report.html', { 'most_sold_products':most_sold_products })

@require_GET
def get_sales_data(request, period):
    print("getting inside inside weew")
    # Your logic to filter and aggregate data based on the selected period
    # Example: Weekly sales
    if period == 'week':
        print("getting inside week")
        start_date = timezone.now().date() - timezone.timedelta(days=6)
        order_items = CartItem.objects.filter(order__date_added__gte=start_date)
        data = (
            order_items.annotate(day=TruncDay('order__date_added'))
            .values('day')
            .annotate(total=Sum(F('quantity') * F('product__price')))
            .order_by('day')
        )
        labels = [item['day'].strftime('%A') for item in data]
        # Example: Monthly sales
    elif period == 'month':
        print("Entering into the month")
        start_date = timezone.now().date() - timezone.timedelta(days=30)
        order_items = CartItem.objects.filter(order__date_added__gte=start_date)
        data = (
        order_items.annotate(day=TruncDay('order__date_added'))
        .values('day')
        .annotate(total=Sum(F('quantity') * F('product__price')))
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
            .annotate(total=Sum(F('quantity') * F('product__price')))
            .order_by('month')
        )
        labels = [f"{item['month'].strftime('%B')}" for item in data]
    else:
        return JsonResponse({'error': 'Invalid period'})

    
    
    sales_data = [item['total'] for item in data]

    return JsonResponse({'labels': labels, 'data': sales_data})

@login_required(login_url='custom_admin_panel:adminlogin')
def sales_details(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('startDate')
        end_date_str = request.POST.get('endDate')
       
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        order_items = CartItem.objects.filter(order__date_added__range=(start_date, end_date), order__isnull=False)
     
        product_quantities = order_items.values('product__product_name').annotate(total_quantity=Sum('quantity'))  

        context = {
            'order_items': order_items,
            'product_quantities': product_quantities,
            'start_date':start_date_str,
            'end_date':end_date_str,

        } 

       
    return render(request, 'custom_admin_panel/salespdf.html', context)

# def generate_sales(request):
#     order = CartItem.objects.all()
#     sales_number = str(random.randint(100000, 999999))


#     context = {
#         'order': order,
#         'sales_number':sales_number,
       
#     }
 

#     pdf = render_to_pdf('custom_admin_panel/salespdf.html', context)
#     if pdf:
#         response = HttpResponse(pdf, content_type='application/pdf')
#         filename =f"sales_{order.id}.pdf"
#         content = "inline; filename='%s'" % filename
#         response['Content-Disposition'] = content
#         return response
#     else:
#         print("Error generating the PDF.")
#         return HttpResponse("Error generating the invoice.")












@never_cache
def admin_logout(request):
    if request.user.is_authenticated and request.user.is_superuser:
        logout(request)
    return redirect('custom_admin_panel:adminlogin')

