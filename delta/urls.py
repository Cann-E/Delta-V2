from django.contrib import admin
from django.urls import path, include
from .views import (
    home_view, upload_signature_view, user_list_view,
    delete_user_view, submit_request, user_requests_view,
    success_page_view, toggle_user_status, inactive_page, inactive,
    change_request_status
)
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # admin panel
    path('', home_view, name='home'),  # home page
    path('users/', user_list_view, name='user_list'),  # show list of users
    path('delete_user/<int:user_id>/', delete_user_view, name='delete_user'),  # delete a user by ID
    path('accounts/', include('allauth.urls')),  # login/logout/signup (Microsoft login)
    
    # Request related URLs
    path('create/<str:request_type>/', views.create_request_view, name='create_request'),  # create request
    path('detail/<int:request_id>/', views.request_detail_view, name='request_detail'),  # request details
    path('submit/<int:request_id>/', views.submit_request_view, name='submit_request'),  # submit request
    path('pending/', views.pending_requests_view, name='pending_requests'),  # pending requests page
    path('approve/<int:request_id>/', views.approve_request_view, name='approve_request'),  # approve request
    path('return/<int:request_id>/', views.return_request_view, name='return_request'),  # return request to student
    
    path('upload-signature/', upload_signature_view, name='upload_signature'),  # upload signature form
    path("submit/", submit_request, name="submit_request"),  # submit a request form
    path("requests/", user_requests_view, name="view_requests"),  # view submitted requests
    path('success/', views.success_page_view, name='success_page'),  # success message/page

    # Change status and toggle user
    path('request/<int:pk>/change-status/', change_request_status, name='change_request_status'),  # manually change request status
    path('users/toggle/<int:user_id>/', toggle_user_status, name='toggle_user_status'),  # activate/deactivate user

    # Inactive user pages
    path('inactive_page/', inactive_page, name='inactive_page'),  # page for inactive users
    path('inactive/', inactive, name='inactive'),  # force inactive users logout
]

# only in debug mode, serve uploaded media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
