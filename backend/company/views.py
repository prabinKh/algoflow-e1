from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        """
        Allow anyone to list and view companies.
        Only authenticated users can create/update.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        from django.contrib.auth.models import Group, Permission
        user = self.request.user
        serializer.save(owner=user)
        
        # Grant vendor permissions
        if not user.is_staff:
            user.is_staff = True
            user.save(update_fields=['is_staff'])
            
        # Add to Vendor group
        vendor_group, created = Group.objects.get_or_create(name='Vendors')
        if created:
            # Add basic permissions for efrontend models and company
            app_models = ['product', 'order', 'orderitem', 'storelocation', 'herosetting', 'company']
            for model_name in app_models:
                perms = Permission.objects.filter(content_type__model=model_name)
                vendor_group.permissions.add(*perms)
        
        user.groups.add(vendor_group)

    def get_queryset(self):
        """
        Filter queryset for standard actions if needed.
        Currently, anyone can see all companies.
        """
        return Company.objects.all().prefetch_related('gallery_images', 'products')

    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def my_companies(self, request):
        """
        Return only the companies owned by the logged-in vendor.
        """
        companies = Company.objects.filter(owner=request.user).prefetch_related('gallery_images')
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)
