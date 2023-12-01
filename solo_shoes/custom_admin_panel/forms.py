from django import forms
from .models import Product,Category,ProductImage
from carts.models import Cart, CartItem
from store.models import Offer, OfferCategory

    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('category_name','is_active','offer',)

class CartsForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = '__all__'

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['delivery_status']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'category', 'price', 'stock', 'description','offer')
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control address-input', 'style': 'color: white;'}),
            'category': forms.Select(attrs={'class': 'form-control address-input', 'style': 'color: white;'}),
            'price': forms.TextInput(attrs={'class': 'form-control address-input', 'style': 'color: white;'}),
            'stock': forms.TextInput(attrs={'class': 'form-control address-input', 'style': 'color: white;'}),
            'description': forms.TextInput(attrs={'class': 'form-control address-input', 'style': 'color: white;'}),
            'offer': forms.Select(attrs={'class': 'form-control address-input', 'style': 'color: white;'}),

            
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('image',)
ProductImageFormSet = forms.inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=4)

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('offer_name','discount_percentage','date_start','date_end','active',)
        widgets = {
            'date_start': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'date_end': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

class OfferCategoryForm(forms.ModelForm):
    class Meta:
        model = OfferCategory
        fields = ('category_offer_name','discount_percentage','date_start','date_end','active',)
        widgets = {
            'date_start': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'date_end': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }





