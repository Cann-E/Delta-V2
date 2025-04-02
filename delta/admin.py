from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

#  Customize how CustomUser appears in the Django admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    #  Columns shown in the user list
    list_display = ('username', 'email', 'role', 'status', 'is_active', 'last_login')
    
    #  Filters shown on the right
    list_filter = ('role', 'status', 'is_active')
    
    #  Add search bar for these fields
    search_fields = ('username', 'email')
    
    #  Default sort order
    ordering = ('role',)
    
    #  Add custom admin action
    actions = ['delete_users']

    #  Fields when viewing/editing a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Status', {'fields': ('status',)}),
    )

    #  Fields when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'status', 'is_active'),
        }),
    )

    #  Custom action to delete users
    def delete_users(self, request, queryset):
        queryset.delete()

    delete_users.short_description = "Delete selected users"

#  Register CustomUser model with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
