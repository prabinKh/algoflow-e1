from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, default='📦')
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, null=True)
    # JSON fields matching Firestore schema
    subcategories = models.JSONField(default=list, blank=True)
    brands = models.JSONField(default=list, blank=True)
    sections = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='brand_list', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    company = models.ForeignKey('company.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    brand_name = models.CharField(max_length=100, blank=True, default='')  # Keep for backward compatibility during migration
    name = models.TextField()
    slug = models.SlugField(max_length=500, unique=True)
    type = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    discount = models.PositiveIntegerField(default=0)
    image = models.URLField()
    gallery = models.JSONField(default=list, blank=True)
    model_3d = models.URLField(blank=True, null=True)
    description = models.TextField()
    specs = models.JSONField(default=list)
    features = models.JSONField(default=list)
    colors = models.JSONField(default=list, blank=True)
    collections = models.JSONField(default=list, blank=True)
    stock = models.PositiveIntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_offer = models.BooleanField(default=False)
    free_shipping = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    reviews_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('online', 'Online'),
    ]
    SOURCE_CHOICES = [
        ('store', 'Store'),
        ('pos', 'POS'),
        ('admin', 'Admin'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey('company.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    uid = models.CharField(max_length=255, blank=True, default='')   # Firebase UID or Django user id str
    order_id = models.CharField(max_length=100, blank=True, default='')  # Human-readable like POS-123456
    email = models.EmailField(blank=True, default='')
    full_name = models.CharField(max_length=200, blank=True, default='')
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, default='Nepal')
    phone = models.CharField(max_length=20, blank=True, default='')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='store')
    customer_type = models.CharField(max_length=50, default='registered')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id or self.id} — {self.full_name or self.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_id_str = models.CharField(max_length=255, blank=True, default='')  # snapshot of product id
    name = models.CharField(max_length=200, blank=True, default='')            # snapshot
    image = models.URLField(blank=True, default='')                            # snapshot
    features = models.JSONField(default=list, blank=True)                      # snapshot
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} x{self.quantity}"


class HeroSetting(models.Model):
    company = models.ForeignKey('company.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='hero_settings')
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    image = models.URLField()
    link = models.CharField(max_length=255)
    specs = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class StoreLocation(models.Model):
    company = models.ForeignKey('company.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='store_locations')
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    opening_hours = models.JSONField(default=dict)


class AIRecommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    query = models.TextField()
    recommendations = models.JSONField()
    reasoning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
