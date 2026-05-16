from django.contrib import admin
from .models import Company, CompanyGalleryImage
from fixitall_backend.admin_site import fixitall_admin

class CompanyGalleryImageInline(admin.TabularInline):
    model = CompanyGalleryImage
    extra = 1

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'storefront_url', 'owner', 'admin_email', 'created_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('name', 'admin_email', 'owner__email', 'owner__name')
    readonly_fields = ('created_at', 'updated_at', 'slug', 'owner')
    inlines = [CompanyGalleryImageInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'logo', 'banner')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address', 'website')
        }),
        ('Vendor Admin Credentials', {
            'description': 'These credentials will be used to create/update the vendor account.',
            'fields': ('admin_name', 'admin_email', 'admin_password', 'owner')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def storefront_url(self, obj):
        from django.utils.html import format_html
        url = f"http://localhost:3000/store/{obj.slug}"
        return format_html('<a href="{}" target="_blank">View Store</a>', url)
    
    storefront_url.short_description = 'Company URL'

fixitall_admin.register(Company, CompanyAdmin)
