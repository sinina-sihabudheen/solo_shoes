
from django.urls import path
from . import views


app_name = 'custom_admin_panel'

urlpatterns = [
    
    path('dashboard/', views.dashboard,name="dashboard"),
    path('',views.admin_login,name='adminlogin'),
    path('adminlogout/',views.admin_logout,name='adminlogout'),


    path('users/search', views.user_management, name='user_management'),
    path('users/block/<int:user_id>/', views.block_user, name='block_user'),
    path('users/unblock<int:user_id>', views.unblock_user, name='unblock_user'),



    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/block/<int:category_id>/', views.block_category, name='block_category'),
    path('categories/unblock/<int:category_id>/', views.unblock_category, name='unblock_category'),
   
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/block/<int:product_id>/', views.block_product, name='block_product'),
    path('products/unblock<int:product_id>/', views.unblock_product, name='unblock_product'),

    path('orders/', views.order, name='order'),
    path('orders/edit/<int:order_item_id>/', views.order_edit, name='order_edit'),
    path('order/cancel_order/<int:order_item_id>/', views.cancel_order, name='cancel_order'),

    path('offer', views.manage_offers_view, name='offer'),
    path('product_off_edit/<int:product_id>/', views.product_off_edit, name='product_off_edit'),
    path('product_off_add/', views.product_off_add, name='product_off_add'),
    path('category_off_edit/<int:category_id>/', views.category_off_edit, name='category_off_edit'),
    path('category_off_add/', views.category_off_add, name='category_off_add'),



   
]




