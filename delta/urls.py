from django.contrib import admin
from django.urls import path, include
from .views import (
    home_view, user_list_view, delete_user_view, check_user_status,
    basic_dashboard_view, submit_request, request_list, deactivate_user,

)

urlpatterns = [
    # Include app-specific URLs
    path("custom_auth/", include("custom_auth.urls")),  # This includes the URLs from your 'custom_auth' app
    path("accounts/", include("allauth.urls")),  # Microsoft login
    path("microsoft/login/", include("allauth.urls")),

    # Define views explicitly
    path("", home_view, name="home_view"),
    path("basic_dashboard/", basic_dashboard_view, name="basic_dashboard"),
    path("admin/", admin.site.urls),
    path("users/", user_list_view, name="user_list"),
    path("delete_user/<int:user_id>/", delete_user_view, name="delete_user"),
    path("submit/", submit_request, name="submit_request"),
    path("list/", request_list, name="request_list"),
    path("deactivate_user/<int:user_id>/", deactivate_user, name="deactivate_user"),
    path("check_user_status/<int:user_id>/", check_user_status, name="check_user_status"),

]
