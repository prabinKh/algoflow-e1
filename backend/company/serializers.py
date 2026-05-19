from rest_framework import serializers
from .models import Company, CompanyGalleryImage
from efrontend.serializers import ProductSerializer

<<<<<<< HEAD

=======
>>>>>>> dev
class CompanyGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGalleryImage
        fields = ['id', 'image', 'created_at']


class CompanySerializer(serializers.ModelSerializer):
    gallery_images = CompanyGalleryImageSerializer(many=True, read_only=True)
<<<<<<< HEAD
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    
    # Write-only field for accepting multiple image URLs during creation/update
=======
    owner_name = serializers.CharField(source='owner.name', read_only=True, default='')
    owner_email = serializers.CharField(source='owner.email', read_only=True, default='')
    product_count = serializers.IntegerField(read_only=True)
    order_count = serializers.IntegerField(read_only=True)
    total_revenue = serializers.FloatField(read_only=True)
>>>>>>> dev
    uploaded_images = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'banner',
<<<<<<< HEAD
            'email', 'phone', 'address', 'website', 'owner', 'owner_name',
            'created_at', 'updated_at', 'gallery_images', 'products', 'uploaded_images'
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        # The owner will be set in the view's perform_create
        company = super().create(validated_data)
        
        for image_url in uploaded_images:
            CompanyGalleryImage.objects.create(company=company, image=image_url)
            
=======
            'email', 'phone', 'address', 'website', 'business_registration',
            'ip_address', 'domain_name',
            'theme_color', 'theme_color_secondary',
            'owner', 'owner_name', 'owner_email',
            'is_active', 'plan', 'created_at', 'updated_at',
            'gallery_images', 'uploaded_images',
            'product_count', 'order_count', 'total_revenue',
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at', 'updated_at', 'product_count', 'order_count', 'total_revenue']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        company = super().create(validated_data)
        for image_url in uploaded_images:
            CompanyGalleryImage.objects.create(company=company, image=image_url)
>>>>>>> dev
        return company

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        company = super().update(instance, validated_data)
<<<<<<< HEAD
        
        for image_url in uploaded_images:
            CompanyGalleryImage.objects.create(company=company, image=image_url)
            
        return company
=======
        for image_url in uploaded_images:
            CompanyGalleryImage.objects.create(company=company, image=image_url)
        return company


class CompanyPublicSerializer(serializers.ModelSerializer):
    """Minimal info for public storefront."""
    gallery_images = CompanyGalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'banner',
            'email', 'phone', 'address', 'website',
            'ip_address', 'domain_name',
            'theme_color', 'theme_color_secondary',
            'gallery_images',
        ]
        read_only_fields = [
            'id', 'name', 'slug', 'description', 'logo', 'banner',
            'email', 'phone', 'address', 'website',
            'ip_address', 'domain_name',
            'theme_color', 'theme_color_secondary'
        ]
>>>>>>> dev
