
from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.carts, name="carts"),
    path('cart/add_cart/<int:product_id>/', views.add_cart, name="add_cart"),
    path('cart/delete_cart/<int:product_id>/', views.remove_cart_item, name="remove_cart_item"),
    path('cart/update_cart/', views.update_cart, name="update_cart"),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/place_order/', views.place_order, name='place_order'),
    path('cart/add_address/', views.add_address, name='add_address'),
    path('order_placed/', views.order_placed, name='order_placed'),
    path('apply_coupon/<int:cart_id>/', views.apply_coupon, name='apply_coupon'),
    path('remove_coupon/<int:cart_id>/', views.remove_coupon, name='remove_coupon'),
    path('proceed_to_pay/', views.razorpaycheck,name='proceed_to_pay'),
    path('place_order_raz/', views.place_order_raz,name='place_order_raz'),
    


]



