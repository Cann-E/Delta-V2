from django import forms
from .models import Request
from .models import CustomUser
from allauth.account.forms import LoginForm
from django.contrib.auth import authenticate
from django.forms import ValidationError
from .models import GeneralPetition

class ChangeMajorForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['current_major', 'new_major']
        # 'status' can be handled by the view logic
        # 'request_type' also can be set in the view

class ChangeAddressForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['old_address', 'new_address']

class SignatureUploadForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['signature']
    
class RequestStatusForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['status']
    
class MyLoginForm(LoginForm):
    def clean(self):
        cleaned_data = super().clean()
        login = cleaned_data.get("login")
        password = cleaned_data.get("password")

        user = authenticate(self.request, username=login, password=password)
        if user and not user.is_active:
            raise ValidationError("This account is currently inactive.")

        return cleaned_data
    




class GeneralPetitionForm(forms.ModelForm):#FOR INTEGRATION
    class Meta:
        model = GeneralPetition
        exclude = ['date_submitted']  
