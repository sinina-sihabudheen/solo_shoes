from django.contrib import admin
from .models import CartItem,Cart,ShoppingCart,Whishlist

# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ['user','date_added']

admin.site.register(Cart,CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product','quantity']

admin.site.register(CartItem,CartItemAdmin)
  
admin.site.register(ShoppingCart)
admin.site.register(Whishlist)

