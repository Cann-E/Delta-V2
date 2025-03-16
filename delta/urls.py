from django.contrib import admin
from django.urls import path, include
from .views import home_view, user_list_view, delete_user_view
from .views import admin_dashboard_view
from .views import developer_dashboard_view
from .views import editor_dashboard_view
from .views import basic_dashboard_view

urlpatterns = [
    path('', home_view, name='home'),
    path('admin_dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('developer_dashboard/', developer_dashboard_view, name='developer_dashboard'),
    path('editor_dashboard/', editor_dashboard_view, name='editor_dashboard'),
    path('basic_dashboard/', basic_dashboard_view, name='basic_dashboard'),
    path('admin/', admin.site.urls),
    path('users/', user_list_view, name='user_list'),  # View users
    path('delete_user/<int:user_id>/', delete_user_view, name='delete_user'),
    path('accounts/', include('allauth.urls')),
]
