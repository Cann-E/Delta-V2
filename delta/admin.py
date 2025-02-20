from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Customize the User Admin page
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'status', 'is_active', 'last_login')
    list_filter = ('role', 'status', 'is_active')  
    search_fields = ('username', 'email')  
    ordering = ('role',)
    actions = ['delete_users']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}), 
        ('Status', {'fields': ('status',)}),  
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'status', 'is_active'),
        }),
    )

    def delete_users(self, request, queryset):
        
        queryset.delete()

    delete_users.short_description = "Delete selected users"
    



admin.site.register(CustomUser, CustomUserAdmin)
