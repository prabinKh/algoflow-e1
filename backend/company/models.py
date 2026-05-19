from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Company(models.Model):
<<<<<<< HEAD
=======
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

>>>>>>> dev
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True, null=True)
    banner = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
<<<<<<< HEAD
    
    admin_name = models.CharField(max_length=200, blank=True, help_text="Admin display name")
    admin_email = models.EmailField(blank=True, help_text="Admin login email")
    admin_password = models.CharField(max_length=128, blank=True, help_text="Admin login password")
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='companies',
        null=True,
        blank=True
    )
    
=======
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
>>>>>>> dev
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
<<<<<<< HEAD
        verbose_name_plural = "Companies"
=======
        verbose_name_plural = 'Companies'
>>>>>>> dev
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
<<<<<<< HEAD
            # Generate a unique slug based on name and a random string to handle duplicate names
            import random, string
            base_slug = slugify(self.name)
            rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            self.slug = f"{base_slug}-{rand_suffix}"
        
        # Sync with owner user if admin info is provided
        if self.admin_email:
            from django.contrib.auth import get_user_model
            from django.contrib.auth.models import Group
            User = get_user_model()
            
            # Use email as username prefix or just use email
            username = self.admin_email.split('@')[0] + "_" + self.slug[:8]
            
            if not self.owner:
                # Create new user
                user, created = User.objects.get_or_create(
                    email=self.admin_email,
                    defaults={
                        'username': username,
                        'name': self.admin_name or self.name,
                        'is_staff': True
                    }
                )
                if created and self.admin_password:
                    user.set_password(self.admin_password)
                    user.save()
                
                # Add to Vendors group
                vendor_group, _ = Group.objects.get_or_create(name='Vendors')
                user.groups.add(vendor_group)
                self.owner = user
            else:
                # Update existing owner if info changed
                user = self.owner
                changed = False
                if self.admin_email and user.email != self.admin_email:
                    user.email = self.admin_email
                    changed = True
                if self.admin_name and user.name != self.admin_name:
                    user.name = self.admin_name
                    changed = True
                if self.admin_password and not user.check_password(self.admin_password):
                    user.set_password(self.admin_password)
                    changed = True
                if changed:
                    user.save()

        super().save(*args, **kwargs)

=======
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

>>>>>>> dev

class CompanyGalleryImage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
<<<<<<< HEAD
        return f"Image for {self.company.name}"
=======
        return f'Image for {self.company.name}'
>>>>>>> dev
