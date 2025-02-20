from django.contrib import admin
from . import views
from django.urls import path, include
from .views import home_view, user_list_view, delete_user_view  
from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView, OAuth2CallbackView

urlpatterns = [
    path('oauth2/callback/', OAuth2CallbackView.adapter_view(MicrosoftGraphOAuth2Adapter), name='microsoft_callback'),
    #path("oauth2/callback/", views.oauth2_callback, name="oauth2_callback"),
    #path('oauth2/callback/', include('allauth.socialaccount.providers.microsoft.urls')),
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', user_list_view, name='user_list'),  # View users
    path('delete_user/<int:user_id>/', delete_user_view, name='delete_user'),  
    path('accounts/', include('allauth.urls')),  
    # Microsoft OAuth2 Callback URL
    
]
