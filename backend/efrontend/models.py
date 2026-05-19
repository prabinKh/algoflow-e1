from django.db import models
<<<<<<< HEAD
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
=======
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from company.models import Company
import uuid

User = get_user_model()

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
>>>>>>> dev

    def __str__(self):
        return self.name


class Brand(models.Model):
<<<<<<< HEAD
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='brand_list', blank=True)
    is_active = models.BooleanField(default=True)
=======
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, related_name='brands', blank=True)
>>>>>>> dev
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

<<<<<<< HEAD
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


=======

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products', db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    brand_name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    specs = models.JSONField(default=dict, blank=True)
    features = models.JSONField(default=list, blank=True)
    colors = models.JSONField(default=list, blank=True)
    collections = models.JSONField(default=list, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.IntegerField(default=0)
    
    image = models.URLField(blank=True, null=True)
    gallery = models.JSONField(default=list, blank=True)
    model_3d = models.URLField(blank=True, null=True)
    
    stock = models.IntegerField(default=0, db_index=True)
    in_stock = models.BooleanField(default=True, db_index=True)
    free_shipping = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_offer = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    
    rating = models.FloatField(default=0)
    reviews_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'slug')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['company', 'created_at']),
        ]

    def __str__(self):
        return f'{self.name} ({self.company.name})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.stock > 0:
            self.in_stock = True
        else:
            self.in_stock = False
        super().save(*args, **kwargs)


>>>>>>> dev
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
<<<<<<< HEAD
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
=======
        ('returned', 'Returned'),
    ]
    PAYMENT_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('cod', 'Cash on Delivery'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uid = models.CharField(max_length=50, unique=True, db_index=True)
    order_id = models.CharField(max_length=50, unique=True, db_index=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders', db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True)
    
    source = models.CharField(max_length=50, blank=True)
    customer_type = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['company', 'created_at']),
            models.Index(fields=['user', 'company']),
        ]

    def __str__(self):
        return f'Order {self.order_id} - {self.company.name}'

    def save(self, *args, **kwargs):
        if not self.uid:
            import uuid
            self.uid = str(uuid.uuid4())
        if not self.order_id:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            import random
            self.order_id = f'ORD{timestamp}{random.randint(1000, 9999)}'
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_id_str = models.CharField(max_length=36, blank=True)
    name = models.CharField(max_length=255)
    image = models.URLField(blank=True, null=True)
    features = models.JSONField(default=dict, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.name} (x{self.quantity})'

    def save(self, *args, **kwargs):
        if self.product:
            self.product_id_str = str(self.product.id)
        super().save(*args, **kwargs)


class HeroSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='hero_setting', null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, null=True)
    cta_text = models.CharField(max_length=100, blank=True, default='Shop Now')
    cta_link = models.CharField(max_length=255, blank=True, default='/products')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Hero - {self.company.name if self.company else "Platform"}'


class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
>>>>>>> dev
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
<<<<<<< HEAD


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
=======
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.email} - {self.product.name}'


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} - {self.rating}★ by {self.user.email}'


class StoreLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.company.name}'


class AIRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.email} - {self.product.name}'
>>>>>>> dev
