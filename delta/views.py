from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django import forms
from django.shortcuts import render, redirect
from .models import AcademicRequest, CustomUser
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib import messages



class AcademicRequestForm(forms.ModelForm):
    class Meta:
        model = AcademicRequest
        fields = ['form_name', 'signature', 'document']


def submit_request(request):
    if request.method == 'POST':
        form = AcademicRequestForm(request.POST, request.FILES)
        if form.is_valid():
            academic_request = form.save(commit=False)
            academic_request.requestor = request.user
            academic_request.save()
            return redirect('request_list')
    else:
        form = AcademicRequestForm()
    return render(request, 'submit_request.html', {'form': form})

@login_required
def request_list(request):
    requests = AcademicRequest.objects.filter(requestor=request.user)
    return render(request, 'request_list.html', {'requests': requests})

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def delete_user_view(request, user_id):

    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect('user_list')

@login_required
@user_passes_test(is_admin)
def user_list_view(request):

    users = CustomUser.objects.all().order_by('username')
    return render(request, 'user_list.html', {'users': users})

@login_required
def home_view(request):
    return render(request, 'home.html', {'user': request.user})

@login_required
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_active:
        user.is_active = False  # Deactivate user
        user.save()
        print(f"❌ User {user.username} has been deactivated.")

    return redirect('user_list')

def check_user_status(request):
    if request.user.is_authenticated and not request.user.is_active:
        logout(request)  # Force logout if deactivated
        return redirect('login')



def basic_dashboard_view(request):
    return render(request, 'dashboard.html')
