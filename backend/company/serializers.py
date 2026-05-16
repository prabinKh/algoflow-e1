from rest_framework import serializers
from .models import Company, CompanyGalleryImage
from efrontend.serializers import ProductSerializer


class CompanyGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGalleryImage
        fields = ['id', 'image', 'created_at']


class CompanySerializer(serializers.ModelSerializer):
    gallery_images = CompanyGalleryImageSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    
    # Write-only field for accepting multiple image URLs during creation/update
    uploaded_images = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'banner',
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
            
        return company

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        company = super().update(instance, validated_data)
        
        for image_url in uploaded_images:
            CompanyGalleryImage.objects.create(company=company, image=image_url)
            
        return company
