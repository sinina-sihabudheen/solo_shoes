from django.contrib import admin
from .models import Category,Product,ProductImage
from .models import Offer, OfferCategory
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name','is_active']

admin.site.register(Category,CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','price','stock','category','modified_date','is_available','offer',]

admin.site.register(Product,ProductAdmin)

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product','image']

admin.site.register(ProductImage,ProductImageAdmin)

admin.site.register(Offer)
admin.site.register(OfferCategory)






