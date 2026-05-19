from django.contrib import admin
from .models import (
    UserActivity, POSSale, ServiceTicket,
    ChatSession, ChatMessage, ContactMessage, CategoryFeature,
    StaffRole, StaffMember,
)
from fixitall_backend.admin_site import fixitall_admin


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'ip_address', 'action')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


class POSSaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_number_display', 'order', 'cashier_display', 'payment_method_display', 'created_at')
    list_filter = ('order__payment_method', 'created_at')
    search_fields = ('transaction_id', 'staff__email')
    readonly_fields = ('created_at',)

    def invoice_number_display(self, obj):
        return obj.transaction_id
    invoice_number_display.short_description = 'Invoice Number'

    def cashier_display(self, obj):
        return obj.staff.email if obj.staff else "N/A"
    cashier_display.short_description = 'Cashier'

    def payment_method_display(self, obj):
        return obj.order.payment_method if obj.order else "N/A"
    payment_method_display.short_description = 'Payment Method'


class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'user', 'title', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('ticket_id', 'user__email', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'priority')
    date_hierarchy = 'created_at'


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('timestamp', 'sender', 'text')
    can_delete = False


class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name_display', 'user_email_display', 'status', 'unread_admin_count', 'unread_user_count', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('email', 'user__email', 'user_id_str')
    inlines = [ChatMessageInline]
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)

    def user_name_display(self, obj):
        return obj.user.username if obj.user else "Guest"
    user_name_display.short_description = 'User Name'

    def user_email_display(self, obj):
        return obj.user.email if obj.user else obj.email
    user_email_display.short_description = 'User Email'


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'text_preview', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('text', 'session__email', 'session__user__email')
    readonly_fields = ('timestamp',)

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Message'


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)


class CategoryFeatureAdmin(admin.ModelAdmin):
    list_display = ('category', 'feature_name', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('feature_name', 'category__name')
    list_editable = ('is_active',)


class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    list_filter = ()
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)


class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'joined_at')
    list_filter = ('is_active', 'role')
    search_fields = ('user__email',)
    readonly_fields = ('joined_at',)


# Register all with custom admin site
fixitall_admin.register(UserActivity, UserActivityAdmin)
fixitall_admin.register(POSSale, POSSaleAdmin)
fixitall_admin.register(ServiceTicket, ServiceTicketAdmin)
fixitall_admin.register(ChatSession, ChatSessionAdmin)
fixitall_admin.register(ChatMessage, ChatMessageAdmin)
fixitall_admin.register(ContactMessage, ContactMessageAdmin)
fixitall_admin.register(CategoryFeature, CategoryFeatureAdmin)
fixitall_admin.register(StaffRole, StaffRoleAdmin)
fixitall_admin.register(StaffMember, StaffMemberAdmin)
