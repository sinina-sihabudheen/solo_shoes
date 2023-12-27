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
    valid_till = models.DateTimeField()
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
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    shopping_cart = models.ForeignKey(ShoppingCart,on_delete=models.CASCADE, null=True, blank=True)

    transaction_id = models.CharField(max_length=200,null=True)


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
    def get_cart_items(self):
        orderitems = self.cartitem_set.all()
        total = sum(item.quantity for item in orderitems)
        
        return total

    
    


    
class CartItem(models.Model):
    product = models.ForeignKey(on_delete=models.SET_NULL, null=True, blank=True, to='custom_admin_panel.Product')    
    order = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True) 
    quantity = models.IntegerField(default=1, null=True, blank=True)
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
    

    
    @property
    def get_total(self):
        # Check if there is an active offer for the product
        product_offer = Offer.objects.filter(product=self.product, active=True).first()

        # Check if there is an active offer for the product category
        category_offer = OfferCategory.objects.filter(category=self.product.category, active=True).first()

        if product_offer and category_offer:
            # If both product and category have offers, choose the greater discount
            discount_percentage = max(product_offer.discount_percentage, category_offer.discount_percentage)
        elif category_offer:
            discount_percentage = category_offer.discount_percentage
        elif product_offer:
            discount_percentage = product_offer.discount_percentage
        else:
            # If no active offer, use the regular product price
            return self.product.price * self.quantity

        # Calculate the discounted price
        discounted_price = self.product.price - (self.product.price * (discount_percentage / 100))
        total = discounted_price * self.quantity
        


        return total



class Whishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlist_products')

    def __str__(self):
        return f"Wishlist for {self.user.username}"
    
