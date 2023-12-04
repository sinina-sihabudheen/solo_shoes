from django.db import models
from django.contrib.auth.models import User

from custom_admin_panel.models import Product

# Create your models here.
class ShippingAddress(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    address_lines = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=15)
    status = models.BooleanField(default=False)

    def _str_(self):
        return self.full_name


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)    
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False,null=True,blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('RAZ', 'Paid With Razorpay'),       
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES,  null=True, blank=True)
    order_notes = models.CharField(max_length=255, blank=True, null=True)  # Add this field
    
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
     
   
    def _str_(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):    
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
        
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)    
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True) 
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
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

    
    # @property
    # def get_total(self):
    #     total = self.product.price * self.quantity
    #     return total
    @property
    def get_total(self):
        product = self.product
        order = self.order

        # Get applicable offers for the product and category
        product_offer = product.offer
        category_offer = product.category.offer if product.category else None

        # Choose the offer with the maximum discount percentage
        if product_offer and category_offer:
            max_discount_percentage = max(product_offer.discount_percentage, category_offer.discount_percentage)
        elif product_offer:
            max_discount_percentage = product_offer.discount_percentage
        elif category_offer:
            max_discount_percentage = category_offer.discount_percentage
        else:
            max_discount_percentage = 0  # No offer applied

        # Calculate discounted price
        if max_discount_percentage > 0:
            discounted_price = product.price - (product.price * max_discount_percentage / 100)
        else:
            discounted_price = product.price

        # Update the product price in the order
        order_item_price = discounted_price * self.quantity
        return order_item_price
