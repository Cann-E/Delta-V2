from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django import forms
from django.shortcuts import render, redirect
from .models import AcademicRequest, CustomUser

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
def role_based_redirect(request):
    user = request.user

    if user.role == 'admin':
        return redirect('admin_dashboard')  # Change to the actual URL name
    elif user.role == 'developer':
        return redirect('developer_dashboard')
    elif user.role == 'editor':
        return redirect('editor_dashboard')
    else:
        return redirect('basic_dashboard')
@login_required
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')
@login_required
def developer_dashboard_view(request):
    return render(request, 'developer_dashboard.html')
@login_required
def editor_dashboard_view(request):
    return render(request, 'editor_dashboard.html')
@login_required
def basic_dashboard_view(request):
    return render(request, 'basic_dashboard.html')