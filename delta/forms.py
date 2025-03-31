from django import forms
from .models import Request
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

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