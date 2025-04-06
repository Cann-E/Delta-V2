from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.contrib import messages
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from delta.notifications import notify_admins

class CustomAccountAdapter(DefaultAccountAdapter):
    def authenticate(self, request, **credentials):
        user = super().authenticate(request, **credentials)
        if user and not user.is_active:
            raise ValidationError(self.error_messages['account_inactive'], code='account_inactive')
        return user

    def respond_user_inactive(self, request, user):
        messages.error(request, self.error_messages['account_inactive'])
        return redirect("inactive_page")
    
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        
        # Check for inactive user and notify admins
        if not user.is_active:
            notify_admins(f"🆕 New user registered: {user.email} ({user.username}) — account pending activation.")
        
        user.save()
        return user
