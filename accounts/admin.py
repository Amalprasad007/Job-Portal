from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'gender', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'gender', 'is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)
    
    # Override fieldsets to remove username field and add our custom fields
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'gender')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Override add_fieldsets to remove username field
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )


admin.site.register(User, UserAdmin)
