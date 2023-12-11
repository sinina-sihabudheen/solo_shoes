from django.contrib import admin

from user_profile.models import Wallet


# Register your models here.

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user','full_name','address_lines','mobile','status']

admin.site.register(Wallet)







