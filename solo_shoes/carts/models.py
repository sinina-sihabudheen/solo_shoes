from django.db import models
from custom_admin_panel.models import Product
from django.contrib.auth.models import User
from store.models import Offer, OfferCategory
from user_profile.models import ShippingAddress
from django.utils import timezone
from django.contrib.auth import get_user_model




# Create your models here.
class ShoppingCart(models.Model):
    session_key = models.CharField(max_length=32, unique=True)

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=20, unique=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_till = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=30))
    is_expired = models.BooleanField(default=False)
    discount_price = models.PositiveIntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)
    # used_by = models.ManyToManyField(User, blank=True) 
    used_by = models.ManyToManyField(get_user_model(), blank=True)
    status = models.BooleanField(default=True)
    
    
    def __str__(self):
        return self.coupon_code
    
    @property
    def has_expired(self):
        return timezone.now() > self.valid_till
    
    def is_user_eligible(self, user):
        return user not in self.used_by.all() 

    def mark_as_used(self, user):
        self.used_by.add(user)
        self.save()   
    


class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    complete = models.BooleanField(default=False, null=True, blank=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL,null=True,blank=True, swappable=True)
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('RAZ', 'Paid With Razorpay'), 
        ('WAL', 'Paid with Wallet'),

    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES,  null=True, blank=True)
    shipping_address_for_orders = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    shopping_cart = models.ForeignKey(ShoppingCart,on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255, default='default_value')
    address_lines = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=15, default='default_value')


    transaction_id = models.CharField(max_length=200,null=True)

    cart_total_at_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cart_items_total_at_order = models.PositiveIntegerField(default=0)
    objects = models.Manager()  # Ensure that the objects manager is defined


    def __str__(self):
        return str(self.id)   
    
    
    
    @property
    def get_cart_total(self):
        orderitems = self.cartitem_set.all()
        total = sum(item.get_total for item in orderitems)
        
        if self.coupon:            
            if self.coupon.minimum_amount <= total:
                return total - self.coupon.discount_price        
        return total
    
    @property
    def get_cart_total_at_order(self):
        orderitems = self.cartitem_set.all()
        total = sum(item.get_total_at_order for item in orderitems)
        
        if self.coupon:            
            if self.coupon.minimum_amount <= total:
                return total - self.coupon.discount_price        
        return total

    @property
    def get_cart_items(self):
        orderitems = self.cartitem_set.all()
        total = sum(item.quantity for item in orderitems)        
        return total

    
    


    
class CartItem(models.Model):
    product = models.ForeignKey(on_delete=models.SET_NULL, null=True, blank=True, to='custom_admin_panel.Product')    
    order = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True) 
    quantity = models.IntegerField(default=1, null=True, blank=True)
    product_name_at_order = models.CharField(max_length=255)  # Store the product name at the time of order placement
    product_description_at_order = models.TextField(blank=True)
    product_price_at_order = models.IntegerField(default=100)
    product_stock_at_order = models.IntegerField(default=0)

    # date_added = models.DateTimeField(auto_now_add=True)
    ORDER_STATUS_CHOICES = [
        ('PL', 'Order placed'),
        ('DS', 'Dispatched'),
        ('SH', 'Shipped'),
        ('OFD', 'Out for Delivery'),
        ('D', 'Delivered'),
        ('CN', 'Order Cancelled'),
        ('RT', 'Returned'),
        ('C', 'Cart Added'),

    ]
    
    delivery_status = models.CharField(max_length=3, choices=ORDER_STATUS_CHOICES, default='C')
    delivery_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)    

    
    @property
    def get_total(self):
        product_offer = Offer.objects.filter(product=self.product, active=True).first()      
        category_offer = OfferCategory.objects.filter(category=self.product.category, active=True).first()

        if product_offer and category_offer:            
            discount_percentage = max(product_offer.discount_percentage, category_offer.discount_percentage)
        elif category_offer:
            discount_percentage = category_offer.discount_percentage
        elif product_offer:
            discount_percentage = product_offer.discount_percentage
        else:          
            return self.product.price * self.quantity
               
        discounted_price = self.product.price - (self.product.price * (discount_percentage / 100))
        total = discounted_price * self.quantity    
        return total
    
    @property
    def get_total_at_order(self):
        
        product_offer = Offer.objects.filter(product=self.product, active=True).first()      
        category_offer = OfferCategory.objects.filter(category=self.product.category, active=True).first()

        if product_offer and category_offer:           
            discount_percentage = max(product_offer.discount_percentage, category_offer.discount_percentage)
        elif category_offer:
            discount_percentage = category_offer.discount_percentage
        elif product_offer:
            discount_percentage = product_offer.discount_percentage
        else:          
            return self.product_price_at_order * self.quantity
      
        discounted_price = self.product_price_at_order - (self.product_price_at_order * (discount_percentage / 100))
        total = discounted_price * self.quantity
        return total

class Whishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlist_products')

    def __str__(self):
        return f"Wishlist for {self.user.username}"
    
