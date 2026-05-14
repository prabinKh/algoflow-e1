from django.core.management.base import BaseCommand
from efrontend.models import Category, Product, HeroSetting
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds the database with initial product data'

    def handle(self, *args, **kwargs):
        # Hero Settings
        hero_data = [
            {
                "title": "Precision Tools for Modern Workflow",
                "subtitle": "Powering performance, built for every ambition. Explore our curated collection of premium electronics.",
                "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=600&fit=crop",
                "link": "/category/laptops-computers",
                "specs": [
                    {"label": "Processor", "value": "Intel® Core™ i5"},
                    {"label": "RAM", "value": "8 GB DDR5"},
                    {"label": "Storage", "value": "512 GB SSD"}
                ],
                "is_active": True,
                "order": 1
            }
        ]
        
        for h_data in hero_data:
            HeroSetting.objects.get_or_create(
                title=h_data['title'],
                defaults=h_data
            )
        self.stdout.write(self.style.SUCCESS('Seeded hero settings'))

        # Categories
        categories_data = [
            {"name": "Laptops & Computers", "slug": "laptops-computers", "icon": "💻"},
            {"name": "Computer Peripherals", "slug": "computer-peripherals", "icon": "🖱️"},
            {"name": "Audio | Headphones", "slug": "audio-headphones", "icon": "🎧"},
            {"name": "Cameras", "slug": "cameras", "icon": "📷"},
            {"name": "Mobiles | Tablets", "slug": "mobiles-tablets", "icon": "📱"},
            {"name": "Home | Kitchen", "slug": "home-kitchen", "icon": "🏠"},
            {"name": "Fitness | Health Care", "slug": "fitness-health", "icon": "💪"},
            {"name": "Car Accessories", "slug": "car-accessories", "icon": "🚗"},
            {"name": "Monitors", "slug": "monitors", "icon": "🖥️"},
        ]

        category_map = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'icon': cat_data['icon']}
            )
            category_map[cat_data['slug']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category "{cat.name}"'))

        # Products
        products_data = [
            {
                "id": "1",
                "name": 'Dell 24 Inch Monitor – SE2422H',
                "slug": "dell-24-inch-monitor-se2422h",
                "category_slug": "monitors",
                "brand": "Dell",
                "price": 23900,
                "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400&h=300&fit=crop",
                "specs": ["24\" FHD", "75Hz", "VA Panel"],
                "description": "Dell 24 inch Full HD monitor with VA panel technology for enhanced color and contrast.",
                "stock": 14,
                "is_new": True,
                "is_best_seller": True,
                "is_popular": True,
                "free_shipping": True,
                "rating": 4.3,
                "reviews_count": 28,
            },
            {
                "id": "2",
                "name": "Dell 24 Inch 200Hz Gaming Monitor",
                "slug": "dell-24-inch-200hz-gaming-monitor",
                "category_slug": "monitors",
                "brand": "Dell",
                "price": 28900,
                "image": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=400&h=300&fit=crop",
                "specs": ["24\" FHD", "200Hz", "IPS"],
                "description": "High-performance 200Hz gaming monitor with IPS panel for smooth, vibrant gameplay.",
                "stock": 8,
                "is_new": True,
                "is_popular": True,
                "rating": 4.7,
                "reviews_count": 45,
            },
            {
                "id": "3",
                "name": "Dell Tower ECT1250 | i5-14400 | 8GB | 512GB",
                "slug": "dell-tower-ect1250-i5-14400",
                "category_slug": "desktop-computers",
                "brand": "Dell",
                "price": 96235,
                "original_price": 127362,
                "discount": 24,
                "image": "https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=400&h=300&fit=crop",
                "specs": ["i5-14400", "8GB DDR5", "512GB SSD"],
                "description": "Dell Tower desktop with Intel i5-14400 processor, perfect for business and productivity.",
                "stock": 6,
                "is_new": True,
                "is_best_seller": True,
                "rating": 4.5,
                "reviews_count": 19,
            },
            {
                "id": "4",
                "name": "Satechi USB-C Magnetic Wireless Charger",
                "slug": "satechi-usb-c-magnetic-wireless",
                "category_slug": "computer-peripherals",
                "brand": "Satechi",
                "price": 3840,
                "original_price": 4800,
                "discount": 20,
                "image": "https://images.unsplash.com/photo-1615526675159-e248c3021d3f?w=400&h=300&fit=crop",
                "specs": ["USB-C", "Magnetic", "15W"],
                "description": "Compact magnetic wireless charger with USB-C connectivity.",
                "stock": 32,
                "free_shipping": True,
                "rating": 4.2,
                "reviews_count": 67,
            },
            {
                "id": "5",
                "name": "Intex 24 Inch FHD Gaming Monitor",
                "slug": "intex-24-inch-fhd-gaming-monitor",
                "category_slug": "monitors",
                "brand": "Intex",
                "price": 15010,
                "original_price": 15800,
                "discount": 5,
                "image": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=400&h=300&fit=crop",
                "specs": ["24\" FHD", "165Hz", "IPS"],
                "description": "Affordable gaming monitor with 165Hz refresh rate.",
                "stock": 11,
                "is_offer": True,
                "rating": 4.0,
                "reviews_count": 33,
            },
            {
                "id": "6",
                "name": "Dell 27 Monitor – SE2725H",
                "slug": "dell-27-monitor-se2725h",
                "category_slug": "monitors",
                "brand": "Dell",
                "price": 25900,
                "image": "https://images.unsplash.com/photo-1551645120-d70bfe84c826?w=400&h=300&fit=crop",
                "specs": ["27\" FHD", "100Hz", "IPS"],
                "description": "Dell 27 inch monitor with IPS panel and thin bezels.",
                "stock": 9,
                "is_new": True,
                "rating": 4.4,
                "reviews_count": 22,
            },
            {
                "id": "7",
                "name": "Acer Aspire Lite 15 Notebook AMD",
                "slug": "acer-aspire-lite-15-amd",
                "category_slug": "laptops-computers",
                "brand": "Acer",
                "price": 51500,
                "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                "specs": ["Ryzen 5", "8GB", "512GB SSD"],
                "description": "Lightweight AMD-powered notebook for everyday computing.",
                "stock": 5,
                "rating": 4.1,
                "reviews_count": 15,
            },
            {
                "id": "8",
                "name": "ASUS Vivobook Go 15 FHD - RYZEN 3",
                "slug": "asus-vivobook-go-15-ryzen3",
                "category_slug": "laptops-computers",
                "brand": "ASUS",
                "price": 42999,
                "original_price": 47200,
                "discount": 9,
                "image": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=300&fit=crop",
                "specs": ["Ryzen 3", "8GB", "256GB SSD"],
                "description": "Budget-friendly ASUS Vivobook with AMD Ryzen 3 processor.",
                "stock": 3,
                "rating": 4.0,
                "reviews_count": 41,
            },
            {
                "id": "9",
                "name": "Lenovo LOQ 15IAX9E Core i5 12450HX",
                "slug": "lenovo-loq-15iax9e-i5",
                "category_slug": "laptops-computers",
                "brand": "Lenovo",
                "price": 125000,
                "image": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400&h=300&fit=crop",
                "specs": ["i5-12450HX", "16GB", "512GB SSD"],
                "description": "Gaming laptop with Intel Core i5 and dedicated NVIDIA graphics.",
                "stock": 4,
                "rating": 4.6,
                "reviews_count": 38,
            },
            {
                "id": "10",
                "name": "Lenovo Legion 5 15AHP10 AMD Ryzen 7",
                "slug": "lenovo-legion-5-ryzen7",
                "category_slug": "laptops-computers",
                "brand": "Lenovo",
                "price": 228000,
                "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&h=300&fit=crop",
                "specs": ["Ryzen 7 260", "16GB", "1TB SSD"],
                "description": "High-performance gaming laptop with AMD Ryzen 7 and RTX graphics.",
                "stock": 2,
                "rating": 4.8,
                "reviews_count": 56,
            },
        ]

        for p_data in products_data:
            cat_slug = p_data.pop('category_slug')
            category = category_map.get(cat_slug)
            if not category:
                # Fallback to general category if specific one not found
                category, _ = Category.objects.get_or_create(slug='general', defaults={'name': 'General', 'icon': '📦'})
            
            p_data['category'] = category
            product, created = Product.objects.get_or_create(
                slug=p_data['slug'],
                defaults=p_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product "{product.name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Product "{product.name}" already exists'))
