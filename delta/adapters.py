from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.contrib import messages
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

class CustomAccountAdapter(DefaultAccountAdapter):
    def authenticate(self, request, **credentials):
        user = super().authenticate(request, **credentials)
        if user and not user.is_active:
            raise ValidationError(self.error_messages['account_inactive'], code='account_inactive')
        return user

    def respond_user_inactive(self, request, user):
        messages.error(request, self.error_messages['account_inactive'])
        return redirect("inactive_page")
