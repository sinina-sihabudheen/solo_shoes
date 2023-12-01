from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'store'

urlpatterns = [
    path('shop/', views.shop, name="shop"),
    path('product/<int:product_id>/', views.product, name='product'),
    path('shop/<str:category>/', views.shop, name='shop_category'),

    path('wishlist/', views.wishlist, name="wishlist"),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
   
]

