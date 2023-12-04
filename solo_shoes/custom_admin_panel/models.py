from typing import Any
from django.db import models
from store.models import Offer,OfferCategory

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    offer = models.ForeignKey(OfferCategory, on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    

    def __str__(self):
        return self.category_name or 'Category'
    
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()    
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)

    
    

    def __str__(self):
        return self.product_name
    
class ProductImage(models.Model):
    image = models.ImageField(upload_to='adminside/assets/images/solo_images/athletics')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    # ,blank=True,null=True

    def __str__(self):
        return self.image.url
    
class Size(models.Model):
    size = models.CharField(max_length=50)    
    
    def _str_(self):
        return self.size

    
class ProductVariance(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    size = models.ForeignKey(Size,on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    def _str_(self):
        return f"{self.product.product_name} - {self.size.size}"


    

    
    