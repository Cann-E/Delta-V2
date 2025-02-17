from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse


def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)  
def delete_user_view(request, user_id):
    
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_list') 

@login_required
@user_passes_test(is_admin)
def user_list_view(request):
   
    users = User.objects.all().order_by('username')  
    return render(request, 'user_list.html', {'users': users})

@login_required
def home_view(request):
    return render(request, 'home.html', {'user': request.user})
