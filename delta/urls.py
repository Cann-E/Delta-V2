from django.contrib import admin
from django.urls import path, include
from .views import home_view, user_list_view, delete_user_view  

urlpatterns = [
    path('admin_dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('developer_dashboard/', developer_dashboard_view, name='developer_dashboard'),
    path('editor_dashboard/', editor_dashboard_view, name='editor_dashboard'),
    path('basic_dashboard/', basic_dashboard_view, name='basic_dashboard'),
]
