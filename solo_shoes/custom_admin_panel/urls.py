
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
    path('categories/search', views.category_management, name='category_management'),
   
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/block/<int:product_id>/', views.block_product, name='block_product'),
    path('products/unblock<int:product_id>/', views.unblock_product, name='unblock_product'),
    path('products/search', views.product_management, name='product_management'),

    path('orders/', views.order, name='order'),
    path('orders/edit/<int:order_item_id>/', views.order_edit, name='order_edit'),
    path('order/cancel_order/<int:order_item_id>/', views.cancel_order, name='cancel_order'),
    path('order/order_details/<int:order_item_id>/', views.order_details, name='order_details'),


    path('offer', views.manage_offers_view, name='offer'),
    path('product_off_edit/<int:offer_id>/', views.product_off_edit, name='product_off_edit'),
    path('product_off_add/', views.product_off_add, name='product_off_add'),
    path('category_off_edit/<int:offer_id>/', views.category_off_edit, name='category_off_edit'),
    path('category_off_add/', views.category_off_add, name='category_off_add'),

    path('sales_report/', views.sales_report, name='sales_report'),
    path('sales_details/', views.sales_details, name='sales_details'),
    
    path('coupon_list/', views.coupon_list, name='coupon_list'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),
    path('edit_coupon/<int:coupon_id>', views.edit_coupon, name='edit_coupon'),
    path('block_coupon/<int:coupon_id>', views.block_coupon, name='block_coupon'),
    path('unblock_coupon/<int:coupon_id>', views.unblock_coupon, name='unblock_coupon'),
    path('toggle_coupon_status/<int:coupon_id>', views.toggle_coupon_status, name='toggle_coupon_status'),

    
   
]




