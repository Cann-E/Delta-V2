from django import forms
from .models import Request
from .models import CustomUser, Unit
from allauth.account.forms import LoginForm
from django.contrib.auth import authenticate
from django.forms import ValidationError
from .models import GeneralPetition
from .models import RCLResponses, TWResponses, Delegation

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


class RCLForm(forms.ModelForm):#FOR INTEGRATION
    class Meta:
        model = RCLResponses
        exclude = ['submission_date', 'is_finalized', 'last_updated']

class TWForm(forms.ModelForm):#FOR INTEGRATION
    class Meta:
        model = TWResponses
        exclude = ['submission_date', 'is_finalized', 'last_updated']
        
class DelegationForm(forms.ModelForm):
    class Meta:
        model = Delegation
        fields = ['delegator', 'delegate', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean(self):
        cleaned = super().clean()
        delegator = cleaned.get('delegator')
        delegate = cleaned.get('delegate')

        if delegator and delegate:
            # ✅ Allow if same unit OR if delegator is admin/org-level approver
            if (delegator.unit == delegate.unit) or delegator.is_superuser or delegator.is_org_approver:
                return cleaned
            else:
                raise forms.ValidationError("Delegation must be within the same unit unless the delegator is an org-level approver.")
        
        return cleaned


class ApproverForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.filter(is_active=True), label="User")
    role = forms.ChoiceField(choices=[
        ('unitapprover', 'Unit Approver'),
        ('admin', 'Org Approver (Admin)'),
    ], label="Role")
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), label="Unit")
    is_org_approver = forms.BooleanField(required=False, label="Organization-wide Approver")

    class Meta:
        model = CustomUser
        fields = ['user', 'role', 'unit', 'is_org_approver']

class ApproverEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role', 'unit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = Unit.objects.all()
        self.fields['unit'].required = False

        if self.instance and self.instance.role == 'admin':
            self.fields['unit'].disabled = True
            self.fields['unit'].empty_label = 'All (Admin)'

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        cleaned['is_org_approver'] = (role == 'admin')
        return cleaned