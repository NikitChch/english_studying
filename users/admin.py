from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'user_type', 'group', 'level', 'is_staff', 'is_active')
    list_filter = ('user_type', 'group', 'level', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_picture')
        }),
        ('Информация о пользователе', {
            'fields': ('user_type', 'group', 'level', 'specialization', 'experience')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 
                      'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                      'user_type', 'group', 'level'),
        }),
    )