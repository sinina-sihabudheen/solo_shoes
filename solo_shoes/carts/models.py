from django.db import models
from custom_admin_panel.models import Product, ProductVariance
from django.contrib.auth.models import User
from user_profile.models import ShippingAddress
from django.utils import timezone


# Create your models here.
class ShoppingCart(models.Model):
    session_key = models.CharField(max_length=32, unique=True)

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    complete = models.BooleanField(default=False, null=True, blank=False)
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),       
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES,  null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    shopping_cart = models.ForeignKey(ShoppingCart,on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
    
    @property
    def get_cart_total(self):
        print("WWWWWWWWWWWW")
        orderitems = self.cartitem.all()
        total = sum([item.get_total for item in orderitems])
        
        return total

    @property
    def get_cart_items(self):
        orderitems = self.cartitem_set.all()
        total = sum(item.quantity for item in orderitems)
        print("total kko so fjfsohfo")
        return total

    
    


    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)    
    variation = models.ForeignKey(ProductVariance, on_delete=models.SET_NULL, null=True, blank=True, related_name='variation') 
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
    ]
    
    delivery_status = models.CharField(max_length=3, choices=ORDER_STATUS_CHOICES, default='PL')

    
    @property
    def get_total(self):
        if hasattr(self, 'discounted_price') and self.discounted_price is not None:
            
            total = self.discounted_price * self.quantity
            print("XXXXXXXXXXX")
        else:
            total = self.product.price * self.quantity
            print("YYYYYYY")
        return total


class Whishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlist_products')

    def __str__(self):
        return f"Wishlist for {self.user.username}"
    
