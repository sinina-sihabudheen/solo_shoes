import re
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django import forms
from django.contrib.auth import get_user_model
from .models import ShippingAddress


class CustomPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        'password_incorrect': "Your old password was entered incorrectly.",
        'password_mismatch': "The two password fields didn't match.",
        'password_minimum_length': "Your password must contain at least 8 characters.",
        'password_common': "Your password can't be a commonly used password.",
        'password_entirely_numeric': "Your password can't be entirely numeric.",
    }

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Your password must contain at least 8 characters.",
    )

    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput,
    )



class CustomUserDetailsForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']



class AddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['id','full_name', 'address_lines', 'city', 'state', 'pin_code', 'country', 'mobile']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control address-input'}),
            'address_lines': forms.TextInput(attrs={'class': 'form-control address-input'}),
            'city': forms.TextInput(attrs={'class': 'form-control address-input'}),
            'state': forms.TextInput(attrs={'class': 'form-control address-input'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control address-input'}),
            'country': forms.TextInput(attrs={'class': 'form-control address-input'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control address-input'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['full_name'].required = True
        self.fields['pin_code'].required = True
        self.fields['mobile'].required = True
        
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        pattern = r'^[6-9]\d{9}$'
    
        if not re.match(pattern, mobile):
            raise forms.ValidationError("Enter a valid mobile number!!!")
        return mobile

