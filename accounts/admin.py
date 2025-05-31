
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('name', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('name',)  # optional: sort by name
    search_fields = ('name', 'email')  # optional: search by name or email

    fieldsets = (
        (None, {'fields': ('name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)