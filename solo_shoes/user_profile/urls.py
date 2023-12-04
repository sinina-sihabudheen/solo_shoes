
from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    path('', views.profile, name="profile"),
    path('changepassword/', views.editpassword, name="editpassword"),
    path('changedetails/', views.editdetails, name="editdetails"),
    path('editaddress/', views.addaddress, name="addaddress"),
    path('editaddress/<int:address_id>/', views.editaddress, name='editaddress'),

    path('deleteaddress/<int:address_id>/', views.deleteaddress, name='deleteaddress'),

    path('myorder/', views.myorder, name='myorder'),
    path('myorder/cancel_order/<int:cart_id>', views.cancel_order, name='cancel_order'),
    path('generate_invoice/<int:cart_id>/', views.generate_invoice, name='generate_invoice'),
   
]
