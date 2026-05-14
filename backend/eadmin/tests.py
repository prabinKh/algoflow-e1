from django.test import TestCase
from efrontend.models import Product, Category, Brand
from .serializers import AdminProductSerializer
from decimal import Decimal

class AdminProductSerializerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Laptops", slug="laptops")
        self.brand = Brand.objects.create(name="Apple", slug="apple")

    def test_serializer_with_ids(self):
        """Test that serializer accepts IDs for brand and category"""
        data = {
            "name": "MacBook Pro",
            "slug": "macbook-pro",
            "category": self.category.id,
            "brand": self.brand.id,
            "price": "1999.99",
            "image": "http://example.com/img.jpg",
            "description": "Powerful laptop"
        }
        serializer = AdminProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.brand, self.brand)

    def test_serializer_with_strings(self):
        """Test that serializer accepts names/slugs for brand and category"""
        data = {
            "name": "MacBook Air",
            "slug": "macbook-air",
            "category": "laptops", # slug
            "brand": "Apple",      # name
            "price": "999.99",
            "image": "http://example.com/img.jpg",
            "description": "Thin laptop"
        }
        serializer = AdminProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.brand, self.brand)

    def test_serializer_with_new_brand_name(self):
        """Test that serializer handles brand names that don't exist yet"""
        data = {
            "name": "New Phone",
            "slug": "new-phone",
            "category": "laptops",
            "brand": "NonExistentBrand",
            "price": "499.99",
            "image": "http://example.com/img.jpg",
            "description": "Unknown brand phone"
        }
        serializer = AdminProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.brand, None)
        self.assertEqual(product.brand_name, "NonExistentBrand")

    def test_price_max_digits(self):
        """Test that larger prices are now accepted (up to 12 digits total)"""
        data = {
            "name": "Luxury Yacht",
            "slug": "luxury-yacht",
            "category": self.category.id,
            "brand": self.brand.id,
            "price": "99999999.99", # 8 digits before decimal
            "image": "http://example.com/img.jpg",
            "description": "Very expensive"
        }
        serializer = AdminProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        # Test 9 digits before decimal (should now work with max_digits=12)
        data["price"] = "123456789.99"
        serializer = AdminProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
