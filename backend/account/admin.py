from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser, LoginAttempt, Note


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'is_admin', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    list_filter = ('is_admin', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('email', 'name', 'firebase_uid')
    ordering = ('-created_at',)
    list_editable = ('is_admin', 'is_staff', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'id')

    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        ('Personal Info', {'fields': ('name', 'username', 'phone_number', 'firebase_uid')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Data', {'fields': ('cart_items', 'wishlist_items')}),
        ('Dates', {'fields': ('created_at', 'updated_at', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_admin'),
        }),
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'ip_address', 'successful', 'attempted_at', 'user_agent')
    list_filter = ('successful', 'attempted_at')
    search_fields = ('email', 'ip_address')
    readonly_fields = ('attempted_at',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')