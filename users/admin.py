from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from agape.admin import admin_site

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Referral info', {'fields': ('referral_code', 'referred_by')}),
        ('Wallets', {
            'fields': (
                'basic1_wallet', 'basic2_wallet', 'standard_wallet',
                'ultimate1_wallet', 'ultimate2_wallet',
                'referral_bonus_wallet', 'funding_wallet'
            )
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

# Register with custom admin site
admin_site.register(User, CustomUserAdmin)
