from django.db import models
from django.conf import settings
from efrontend.models import Product, Order, Category


class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    page_type = models.CharField(max_length=100)
    path = models.CharField(max_length=500)
    duration = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    user_agent = models.TextField(blank=True)
    screen_resolution = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']


class POSSale(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='pos_sale')
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=50, default='cash')
    invoice_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number


class ServiceTicket(models.Model):
    STATUS_CHOICES = [
        ('Received', 'Received'),
        ('Diagnosing', 'Diagnosing'),
        ('In Progress', 'In Progress'),
        ('In Repair', 'In Repair'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ticket_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    component = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    service_type = models.CharField(max_length=50, default='Carry-in')
    address = models.TextField(blank=True)
    current_location = models.CharField(max_length=200, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    contact_channel = models.CharField(max_length=50, default='chat')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Received')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.ticket_id} - {self.brand} {self.model}'

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            import random, string
            rand = ''.join(random.choices(string.digits, k=6))
            self.ticket_id = f'TKT-{rand}'
        super().save(*args, **kwargs)


class ChatSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('handoff', 'Handoff'),
        ('archived', 'Archived'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    user_id_str = models.CharField(max_length=255, help_text='For guest users', blank=True, default='')
    user_name = models.CharField(max_length=100, default='Guest', blank=True)
    user_email = models.CharField(max_length=255, blank=True, null=True)  # CharField allows 'Guest' and any string
    last_message = models.TextField(blank=True)
    last_message_time = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    unread_admin_count = models.PositiveIntegerField(default=0)
    unread_user_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Chat {self.id} - {self.user_name}'


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('human', 'Human'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')
    msg_type = models.CharField(max_length=20, default='text')
    attachments = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['timestamp']


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.subject}'


class CategoryFeature(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='features_list')
    feature_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('category', 'feature_name')

    def __str__(self):
        return f'{self.category.name} - {self.feature_name}'


class StaffRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list)
    color = models.CharField(max_length=50, default='bg-emerald-500')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StaffMember(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    role = models.ForeignKey(
        StaffRole,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='staff_members'
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.URLField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} — {self.role.name if self.role else 'No Role'}"
