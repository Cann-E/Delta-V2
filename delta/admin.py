from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Notification, Unit, Delegation

# Customize the User Admin page
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_org_approver', 'status', 'is_active', 'last_login')
    list_filter = ('role', 'status', 'is_active')  
    search_fields = ('username', 'email')  
    ordering = ('role',)
    actions = ['delete_users']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'unit', 'is_org_approver')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}), 
        ('Status', {'fields': ('status',)}),  
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'status', 'is_active', 'is_org_approver', 'unit'),
        }),
    )

    def delete_users(self, request, queryset):
        queryset.delete()

    delete_users.short_description = "Delete selected users"

    
admin.site.register(CustomUser, CustomUserAdmin)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    
@admin.register(Delegation)
class DelegationAdmin(admin.ModelAdmin):
    list_display = ('delegator', 'delegate', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')