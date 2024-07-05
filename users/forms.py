from django import forms
from django.forms import ModelForm, TextInput, EmailInput
from users.models import User, UserProfile
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django_countries.widgets import CountrySelectWidget

# Create a UserUpdateForm to update username and email
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField() 

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'email': EmailInput(attrs={
                'class': "email", 
                'placeholder': 'Email'
            })
        }

class ProfileUpdateForm_c(forms.ModelForm):
    phone_number = PhoneNumberField(
            widget=PhoneNumberPrefixWidget(initial='KE', attrs={'class': 'p-no'})
        ) 
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'country']

# Create a ProfileUpdateForm to update image
class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ['gender', 'image']

# Create a ProfileUpdateForm to update description
class ProfileUpdateForm_desc(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['description']
