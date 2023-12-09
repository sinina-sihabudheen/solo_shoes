from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'user_authentication'

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.loginn, name="login"),
    path('otp_verification/', views.otp_verification, name='otp_verification'),
    path('signout', views.signout,name='signout'),
    path('forgot_paswrd', views.forgot_password, name='forgot_password'),
    path('paswrd_otp', views.password_otp_verification, name='password_otp'),
    path('set_paswrd', views.set_password, name='set_password'),
    path('resend_otp', views.resend_otp, name='resend_otp'),
    path('resend_register_otp', views.resend_register_otp, name='resend_register_otp'),
]

