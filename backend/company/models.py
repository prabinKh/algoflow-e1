from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Company(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True, null=True)
    banner = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    
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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
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


class CompanyGalleryImage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.company.name}"
