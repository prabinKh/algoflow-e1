from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Company(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True, null=True)
    banner = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    business_registration = models.CharField(max_length=200, blank=True)
    ip_address = models.CharField(max_length=50, blank=True, null=True, unique=True)
    domain_name = models.CharField(max_length=255, blank=True, null=True, unique=True)

    # Branding
    theme_color = models.CharField(max_length=20, default='#6366f1')
    theme_color_secondary = models.CharField(max_length=20, default='#4f46e5')

    # Admin credentials (for seeding / display)
    admin_name = models.CharField(max_length=200, blank=True)
    admin_email = models.EmailField(blank=True)
    admin_password = models.CharField(max_length=128, blank=True)

    # Linked Django user (company admin)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='owned_companies',
        null=True,
        blank=True,
    )

    # Platform metadata
    is_active = models.BooleanField(default=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            import random, string
            base_slug = slugify(self.name)
            rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            self.slug = f'{base_slug}-{rand_suffix}'
        super().save(*args, **kwargs)

    @property
    def product_count(self):
        return self.products.count()

    @property
    def order_count(self):
        return self.orders.count()

    @property
    def total_revenue(self):
        from django.db.models import Sum
        result = self.orders.filter(status='delivered').aggregate(
            total=Sum('total_amount'))['total']
        return float(result or 0)

    @classmethod
    def resolve_from_request(cls, request):
        # 1. Try company slug or ID from query parameter
        company_param = None
        if hasattr(request, 'query_params'):
            company_param = request.query_params.get('company')
        if not company_param and hasattr(request, 'GET'):
            company_param = request.GET.get('company')
            
        if company_param:
            if str(company_param).isdigit():
                comp = cls.objects.filter(models.Q(slug=company_param) | models.Q(id=int(company_param)) | models.Q(ip_address=company_param) | models.Q(domain_name=company_param)).first()
            else:
                comp = cls.objects.filter(models.Q(slug=company_param) | models.Q(ip_address=company_param) | models.Q(domain_name=company_param)).first()
            if comp:
                return comp

        # 2. Try to resolve by host/IP from headers (X-Forwarded-Host or Host)
        host = None
        if hasattr(request, 'META'):
            host = request.META.get('HTTP_X_FORWARDED_HOST')
            print("resolve_from_request HTTP_X_FORWARDED_HOST:", host)
            print("resolve_from_request HTTP_HOST:", request.META.get('HTTP_HOST'))
            print("resolve_from_request REMOTE_ADDR:", request.META.get('REMOTE_ADDR'))
        if not host:
            host = request.get_host() if hasattr(request, 'get_host') else ''
            
        # Extract IP or domain (remove port if present)
        ip_or_domain = host.split(':')[0].strip() if host else ''
        print("resolve_from_request ip_or_domain parsed:", ip_or_domain)
        if ip_or_domain:
            comp = cls.objects.filter(models.Q(ip_address=ip_or_domain) | models.Q(slug=ip_or_domain) | models.Q(domain_name=ip_or_domain)).first()
            if comp:
                print("resolve_from_request resolved company:", comp.name)
                return comp

        # 3. Fallback to owner's company if authenticated
        if hasattr(request, 'user') and request.user and request.user.is_authenticated and getattr(request.user, 'company', None):
            return request.user.company

        # 4. Global default fallback
        fallback = cls.objects.first()
        print("resolve_from_request falling back to first:", fallback.name if fallback else "None")
        return fallback


class CompanyGalleryImage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.company.name}'
