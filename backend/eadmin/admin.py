from django.contrib import admin
from .models import (
    UserActivity, POSSale, ServiceTicket,
    ChatSession, ChatMessage, ContactMessage, CategoryFeature
)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'page_type', 'path', 'duration', 'timestamp')
    list_filter = ('page_type', 'timestamp')
    search_fields = ('email', 'path', 'user__email')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(POSSale)
class POSSaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'cashier', 'payment_method', 'created_at')
    list_filter = ('payment_method', 'created_at')
    search_fields = ('invoice_number', 'cashier__email')
    readonly_fields = ('created_at',)


@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'user', 'category', 'brand', 'model', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'service_type', 'category', 'created_at')
    search_fields = ('ticket_id', 'user__email', 'brand', 'model', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'priority')
    date_hierarchy = 'created_at'


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('timestamp', 'sender', 'text')
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'user_email', 'status', 'unread_admin_count', 'unread_user_count', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user_name', 'user_email', 'user_id_str')
    inlines = [ChatMessageInline]
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'text_preview', 'timestamp', 'status')
    list_filter = ('sender', 'status', 'timestamp')
    search_fields = ('text', 'session__user_name', 'session__user_email')
    readonly_fields = ('timestamp',)

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Message'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)


@admin.register(CategoryFeature)
class CategoryFeatureAdmin(admin.ModelAdmin):
    list_display = ('category', 'feature_name', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('feature_name', 'category__name')
    readonly_fields = ('created_at',)
    list_editable = ('is_active',)
