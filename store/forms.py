from django import forms
from .models import CustomUser, Product


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProductForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    stock = forms.IntegerField()


class UserCartAddForm(forms.Form):
    product_id = forms.IntegerField()


class UserCartRemoveForm(forms.Form):
    product_id = forms.IntegerField()


class UserUpdateForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    latitude = forms.FloatField()
    longitude = forms.FloatField()


class FarmUpdateForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea)
    latitude = forms.FloatField()
    longitude = forms.FloatField()

