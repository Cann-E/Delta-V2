from django.contrib import admin
from django.urls import path, include
from .views import home_view, user_list_view, delete_user_view  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', user_list_view, name='user_list'),  # View users
    path('delete_user/<int:user_id>/', delete_user_view, name='delete_user'),  
    path('accounts/', include('allauth.urls')),  
]
