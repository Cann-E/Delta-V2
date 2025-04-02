from django import forms
from .models import Request
from .models import CustomUser

#  form to change major
class ChangeMajorForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['current_major', 'new_major']  # user fills these
        # 'status' and 'request_type' are handled in the view

#  form to change address
class ChangeAddressForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['old_address', 'new_address']

#  form to upload signature image
class SignatureUploadForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['signature']  # user uploads image file

#  admin form to update request status
class RequestStatusForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['status']  # change to draft, pending, approved, etc.
