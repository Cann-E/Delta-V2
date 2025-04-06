from django.contrib import admin
from django.urls import path, include
from .views import (
    home_view, user_list_view, delete_user_view, check_user_status,
     submit_request,  deactivate_user,

)
from django.contrib import admin
from django.urls import path, include
from .views import home_view, upload_signature_view, user_list_view, delete_user_view,submit_request,user_requests_view,success_page_view
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import change_request_status,request_list_view

urlpatterns = [
    # Include app-specific URLs
    path("custom_auth/", include("custom_auth.urls")),  # This includes the URLs from your 'custom_auth' app
    path("accounts/", include("allauth.urls")),  # Microsoft login
    path("microsoft/login/", include("allauth.urls")),

    # Define views explicitly
    path("", home_view, name="home_view"),
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),

    path('delete_user/<int:user_id>/', delete_user_view, name='delete_user'),

    path('create/<str:request_type>/', views.create_request_view, name='create_request'),
    path('detail/<int:request_id>/', views.request_detail_view, name='request_detail'),
    path('submit/<int:request_id>/', views.submit_request_view, name='submit_request'),
    path('pending/', views.pending_requests_view, name='pending_requests'),
    path('approve/<int:request_id>/', views.approve_request_view, name='approve_request'),
    path('return/<int:request_id>/', views.return_request_view, name='return_request'),
    path('upload-signature/', upload_signature_view, name='upload_signature'),

    path("requests/", user_requests_view, name="view_requests"),
    path('success/', views.success_page_view, name='success_page'),
    path('request/<int:pk>/change-status/', change_request_status, name='change_request_status'),


    path("users/", user_list_view, name="user_list"),
    path("delete_user/<int:user_id>/", delete_user_view, name="delete_user"),
    path("submit/", submit_request, name="submit_request"),
    path("list/", request_list_view, name="request_list"),
    path("deactivate_user/<int:user_id>/", deactivate_user, name="deactivate_user"),
    path("check_user_status/<int:user_id>/", check_user_status, name="check_user_status"),

]
