
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
    path('cart/order_placed/', views.order_placed, name='order_placed'),
    


]



