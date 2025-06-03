
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('name', 'email', 'mobile', 'pincode', 'city', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('name',)
    search_fields = ('name', 'email', 'mobile', 'city', 'pincode')

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'mobile', 'pincode', 'city', 'address', 'password')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'email', 'mobile', 'pincode', 'city', 'address',
                'password1', 'password2', 'is_staff', 'is_active'
            )
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)