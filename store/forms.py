from django import forms

from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm


#here UserCreationForm have two fileds a,validation and password encryipttion

class SignUpForm(UserCreationForm):

    class Meta:

        model=User

        fields=["username","email","password1","password2"]


class SignInForm(forms.Form):

    username=forms.CharField(max_length=200)

    password=forms.CharField(widget=forms.PasswordInput())