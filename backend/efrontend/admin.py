from django.contrib import admin
from .models import Category, Product, Order, OrderItem, HeroSetting, Wishlist, Review, StoreLocation


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_id_str', 'name', 'image', 'quantity', 'price')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock', 'in_stock', 'is_new', 'rating', 'created_at')
    list_filter = ('category', 'brand', 'in_stock', 'is_new', 'is_best_seller', 'is_popular', 'is_offer')
    search_fields = ('name', 'brand', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock', 'in_stock')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'full_name', 'email', 'total_amount', 'status', 'payment_status', 'payment_method', 'source', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'source', 'created_at')
    search_fields = ('order_id', 'full_name', 'email', 'phone')
    list_editable = ('status', 'payment_status')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'quantity', 'price')
    search_fields = ('name', 'order__order_id')


@admin.register(HeroSetting)
class HeroSettingAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__email', 'comment')
    readonly_fields = ('created_at',)


@admin.register(StoreLocation)
class StoreLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'email')
    search_fields = ('name', 'city')
