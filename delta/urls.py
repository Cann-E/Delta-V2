from django.contrib import admin
from django.urls import path, include
from .views import home_view, upload_signature_view, user_list_view, delete_user_view,submit_request,user_requests_view,success_page_view, toggle_user_status,inactive_page,inactive, toggle_read_status, unread_count_view, unread_count
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import change_request_status, CustomLoginView
from delta.views import microsoft_login, microsoft_callback, microsoft_logout
from .views import general_petition_view
from .views import petition_success
from .views import rcl_form_view, tw_form_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', user_list_view, name='user_list'),  # View users
    path('delete_user/<int:user_id>/', delete_user_view, name='delete_user'),  
    path('accounts/', include('allauth.urls')), 
    path("accounts/login/", CustomLoginView.as_view(), name="account_login"), 
    path('create/<str:request_type>/', views.create_request_view, name='create_request'),
    path('detail/<int:request_id>/', views.request_detail_view, name='request_detail'),
    path('submit/<int:request_id>/', views.submit_request_view, name='submit_request'),
    path('pending/', views.pending_requests_view, name='pending_requests'),
    path('approve/<int:request_id>/', views.approve_request_view, name='approve_request'),
    path('return/<int:request_id>/', views.return_request_view, name='return_request'),
    path('upload-signature/', upload_signature_view, name='upload_signature'),
    path("submit/", submit_request, name="submit_request"),
    path("requests/", user_requests_view, name="view_requests"),
    path('success/', views.success_page_view, name='success_page'),
    path('request/<int:pk>/change-status/', change_request_status, name='change_request_status'),
    path('users/toggle/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('inactive_page/', inactive_page, name='inactive_page'),
    path('inactive/', inactive, name='inactive'),
    path('login/microsoft/', microsoft_login, name='microsoft-login'),
    path("login/microsoft/callback/", microsoft_callback, name="microsoft-callback"),
    path('logout/', microsoft_logout, name='microsoft-logout'),
    path('notifications/', views.view_notifications, name='view_notifications'),
    path('notifications/toggle/<int:notification_id>/', toggle_read_status, name='toggle_read_status'),
    path('notifications/unread-count/', unread_count_view, name='unread_count'),
    path('notifications/unread-count/', unread_count, name='unread_count'),
    path('notifications/delete/', views.delete_notifications, name='delete_notifications'),
    path('petition/', general_petition_view, name='general_petition'),#FOR INTEGRATION
    path('petition/success/', petition_success, name='petition_success'),#FOR INTEGRATION#FOR INTEGRATION
    path('rcl/', rcl_form_view, name='rcl_form'),#FOR INTEGRATION
    path('tw/', tw_form_view, name='tw_form'),#FOR INTEGRATION
    path('rcl/success/', views.success_page_view, name='rcl_success'),#FOR INTEGRATION
    path('tw/success/', views.success_page_view, name='tw_success'),#FOR INTEGRATION
    path("submit/rcl/", views.submit_rcl, name="submit_rcl"),#FOR INTEGRATION
    path('download/<str:obj_type>/<int:object_id>/', views.download_pdf, name='download_pdf'),

    path("submit/tw/", views.submit_tw, name="submit_tw"),#FOR INTEGRATION
    path('tw/download/<int:response_id>/', views.download_tw_pdf, name='download_tw_pdf'),#FOR INTEGRATION
    path('request/preview/<int:request_id>/', views.preview_request_pdf, name='preview_request_pdf'),
    path('petition/preview/<int:request_id>/', views.preview_general_petition_pdf, name='preview_general_petition_pdf'),
    path('request/download/<int:request_id>/', views.download_request_pdf, name='download_request_pdf'),
    path('preview/<str:obj_type>/<int:object_id>/', views.preview_pdf, name='preview_pdf'),
    path('tw/preview/<int:pk>/', views.preview_tw_pdf, name='preview_tw_pdf')#FOR INTEGRATION








]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
