from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.text import slugify
from company.models import Company
from efrontend.models import Product, Category
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with 5 companies and 25 products for multi-vendor testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Wiping existing companies and products..."))
        
        # Delete existing data
        Company.objects.all().delete()
        Product.objects.all().delete()
        # Delete users that start with 'vendor_'
        User.objects.filter(username__startswith='vendor_').delete()

        # Ensure we have a default category
        category, _ = Category.objects.get_or_create(
            name="General Electronics",
            defaults={'slug': 'general-electronics', 'description': 'Default category for seeded products'}
        )
        
        # Ensure Vendor group exists
        vendor_group, _ = Group.objects.get_or_create(name='Vendors')

        companies_created = []

        for i in range(1, 6):
            company_name = f'Company {chr(64+i)} Tech'
            admin_email = f'vendor{i}@example.com'
            
            # Create Company (This will auto-create the User via save() override)
            company = Company.objects.create(
                name=company_name,
                admin_name=f'Vendor {i}',
                admin_email=admin_email,
                admin_password='password123',
                description=f'This is a seeded company for {company_name}',
                email=admin_email,
                phone=f'555-010{i}',
            )
            companies_created.append(company)
            self.stdout.write(self.style.SUCCESS(f"Created Company: {company_name} (Admin: {admin_email})"))

            # 3. Create 5 Products for this company
            for j in range(1, 6):
                product_name = f'{company_name} Product {j}'
                Product.objects.create(
                    company=company,
                    category=category,
                    name=product_name,
                    slug=slugify(f"{company_name}-product-{j}-{random.randint(1000, 9999)}"),
                    price=random.randint(99, 999) + 0.99,
                    description=f'High quality product {j} from {company_name}.',
                    image='https://picsum.photos/seed/product/400/400',
                    stock=50,
                    in_stock=True
                )
            
            self.stdout.write(self.style.SUCCESS(f"  -> Added 5 products to {company_name}"))

        self.stdout.write(self.style.SUCCESS("\n=================================================="))
        self.stdout.write(self.style.SUCCESS("Database Seeding Complete!"))
        self.stdout.write(self.style.SUCCESS("You can view the storefronts at:"))
        for c in companies_created:
            self.stdout.write(f"http://localhost:3000/store/{c.slug}")
        self.stdout.write(self.style.SUCCESS("=================================================="))
