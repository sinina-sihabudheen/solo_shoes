from django.forms import ValidationError
from django.utils import timezone
from django.db import models
# from custom_admin_panel.models import Product, Category

# Create your models here.
class Offer(models.Model):
    
    offer_name = models.CharField(max_length=255)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    date_start = models.DateTimeField(default=timezone.now)
    date_end = models.DateTimeField()
    active = models.BooleanField(default=False)

    

    
    def __str__(self):
        return self.offer_name

class OfferCategory(models.Model):
    
    category_offer_name = models.CharField(max_length=255)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    date_start = models.DateTimeField(default=timezone.now)
    date_end = models.DateTimeField()
    active = models.BooleanField(default=False)

    


    

    def __str__(self):
        return self.category_offer_name



