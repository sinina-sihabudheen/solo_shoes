from django.contrib import admin
from .models import ShippingAddress,Order,OrderItem

# Register your models here.

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user','full_name','address_lines','mobile','status']

admin.site.register(ShippingAddress,ShippingAddressAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer','date_ordered','payment_method','shipping_address']

admin.site.register(Order,OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product','date_added','quantity','delivery_status']

admin.site.register(OrderItem,OrderItemAdmin)




