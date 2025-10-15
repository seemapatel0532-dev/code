from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField,PasswordChangeForm,SetPasswordForm,PasswordResetForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from .models import Vendor,Product,Review

from .models import Customer
 
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus':'True','class':'form-control'}))
    password = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'form-control'}))

class CustomerRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus':'True','class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'form-control','id': 'password'}))
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'class':'form-control','id': 'password'}))

    class Meta:
        model = User
        fields = ["username","email","password1","password2"]

class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email does not exist.")
        return email
    # username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # def clean_username(self):
    #     username = self.cleaned_data.get('username')
    #     if not User.objects.filter(username=username).exists():
    #         raise forms.ValidationError("This username does not exist.")
    #     return username


class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password',widget=forms.PasswordInput(attrs={'autofocus':'True','autocomplete':'current-password','class':'form-control'}))
    new_password1 = forms.CharField(label='New Password',widget=forms.PasswordInput(attrs={'autofocus':'True','autocomplete':'current-password','class':'form-control'}))
    new_password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'autofocus':'True','autocomplete':'current-password','class':'form-control'}))


# forms.py
from django import forms
from django.core.validators import RegexValidator
from .models import Customer

class CustomerProfile(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ['name', 'locality', 'city', 'mobile', 'state', 'zipcode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'locality': forms.TextInput(attrs={'class': 'form-control'}), 
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'zipcode': forms.NumberInput(attrs={'class': 'form-control'}),
            'mobile': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def clean_mobile(self):
        mobile = str(self.cleaned_data.get('mobile'))
        if len(mobile) != 10 or not mobile.startswith(('7', '8', '9')):
            raise ValidationError("Mobile number must be a 10 digit number starting with 7, 8, or 9.")
        return int(mobile)

    def clean_zipcode(self):
        zipcode = self.cleaned_data.get('zipcode')
        if zipcode < 100000 or zipcode > 999999:
            raise ValidationError("Zipcode must be a 6 digit number between 100000 and 999999.")
        return zipcode


class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'contact_number', 'location', 'status']
        widgets = {
            'vendor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_contact_number(self):
        contact_number = str(self.cleaned_data.get('contact_number'))
        if len(contact_number) != 10 or not contact_number.startswith(('7', '8', '9')):
            raise ValidationError("Contact number must be a 10 digit number starting with 7, 8, or 9.")
        return contact_number
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['vendor', 'created_at']  # Exclude vendor and created_at, as vendor will be assigned in the view
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image_url' : forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ['product']
        #fields = ['product', 'name', 'rating', 'review_text']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control '}, choices=[(i, str(i)) for i in range(1, 6)]),
            'review_text': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control'}),
        }
        labels = {
            'review_text': 'Your Review',
        }
    


    