from django.utils import timezone
from django import forms
from .models import Product,Category,ProductImage
from carts.models import Cart, CartItem, Coupon
from store.models import Offer, OfferCategory



class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('coupon_code', 'valid_from', 'valid_till', 'discount_price', 'minimum_amount',)
        widgets = {
            'coupon_code': forms.TextInput(attrs={'class': 'form-control ', 'style': 'color: white;'}),
            'valid_from': forms.TextInput(attrs={'type': 'datetime-local','class': 'form-control ', 'style': 'color: white;'}),
            'valid_till': forms.TextInput(attrs={'type': 'datetime-local','class': 'form-control ', 'style': 'color: white;'}),
            'discount_price': forms.TextInput(attrs={'class': 'form-control ', 'style': 'color: white;'}),
            'minimum_amount': forms.TextInput(attrs={'class': 'form-control ', 'style': 'color: white;'}),
            
                        
        }
    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_till = cleaned_data.get('valid_till')
        minimum_amount = cleaned_data.get('minimum_amount')

        # Check if end date is greater than start date
        if valid_from and valid_till and valid_from >= valid_till:
            raise forms.ValidationError("End date must be greater than the start date.")

        # Check if minimum_amount is negative
        if minimum_amount is not None and minimum_amount < 0:
            raise forms.ValidationError("Minimum amount should not be negative.")

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valid_from'].input_formats = ['%Y-%m-%dT%H:%M', ]  
        self.fields['valid_till'].input_formats = ['%Y-%m-%dT%H:%M', ]    
    
    
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
        widgets = {
            'delivery_status' : forms.Select(attrs={'class': 'form-control address-input', 'style': 'color: white;'})
        }

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
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price should not be negative.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock should not be negative.")
        return stock
    
    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        is_editing = self.instance and self.instance.pk is not None  # Check if in edit mode

        if not is_editing and Product.objects.filter(product_name=product_name).exists():
            raise forms.ValidationError("Product with this name already exists.")

        return product_name




class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('image',)
ProductImageFormSet = forms.inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=4)

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('offer_name','discount_percentage','date_start','date_end',)
        widgets = {
            'offer_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: white;'}),
            'discount_percentage': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: white;'}),
            'date_start': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'style': 'color: white;'}),
            'date_end': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'style': 'color: white;'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')

        # Check if end date is greater than start date
        if date_start and date_end and date_start >= date_end:
            raise forms.ValidationError("End date must be greater than the start date.")


        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_start'].input_formats = ['%Y-%m-%dT%H:%M', ]  
        self.fields['date_end'].input_formats = ['%Y-%m-%dT%H:%M', ]    
    

class OfferCategoryForm(forms.ModelForm):
    class Meta:
        model = OfferCategory
        fields = ('category_offer_name','discount_percentage','date_start','date_end',)
        widgets = {
            'category_offer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'discount_percentage': forms.TextInput(attrs={'class': 'form-control'}),
            'date_start': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'date_end': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage is not None and discount_percentage < 0:
            raise forms.ValidationError("Discount percentage should not be negative.")
        return discount_percentage
    
    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')

        # Check if end date is greater than start date
        if date_start and date_end and date_start >= date_end:
            raise forms.ValidationError("End date must be greater than the start date.")

        return cleaned_data

   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_start'].input_formats = ['%Y-%m-%dT%H:%M', ]  
        self.fields['date_end'].input_formats = ['%Y-%m-%dT%H:%M', ]    

    

