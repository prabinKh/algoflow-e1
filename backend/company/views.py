<<<<<<< HEAD
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
=======
from rest_framework import viewsets, permissions, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Company, CompanyGalleryImage
from .serializers import CompanySerializer, CompanyPublicSerializer

User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
>>>>>>> dev
    serializer_class = CompanySerializer
    lookup_field = 'slug'

    def get_permissions(self):
<<<<<<< HEAD
        """
        Allow anyone to list and view companies.
        Only authenticated users can create/update.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
=======
        if self.action in ['list', 'retrieve', 'public_info']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Company.objects.filter(is_active=True).prefetch_related('gallery_images')
>>>>>>> dev

    def perform_create(self, serializer):
        from django.contrib.auth.models import Group, Permission
        user = self.request.user
        serializer.save(owner=user)
<<<<<<< HEAD
        
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
=======
        if not user.is_staff:
            user.is_staff = True
            user.save(update_fields=['is_staff'])
        vendor_group, created = Group.objects.get_or_create(name='Vendors')
        user.groups.add(vendor_group)

    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def my_companies(self, request):
        companies = Company.objects.filter(owner=request.user).prefetch_related('gallery_images')
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], permission_classes=[permissions.AllowAny], url_path='public')
    def public_info(self, request, slug=None):
        try:
            company = Company.objects.get(slug=slug, is_active=True)
        except Company.DoesNotExist:
            return Response({'detail': 'Store not found or inactive.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyPublicSerializer(company)
        return Response(serializer.data)


class CompanyProfileView(views.APIView):
    """Company admin can view/update their own company profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            return Response({'detail': 'No company associated.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def patch(self, request):
        company = request.user.company
        if not company:
            return Response({'detail': 'No company associated.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role not in ('company_admin', 'superadmin') and not request.user.is_superuser:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'company': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class StoreInfoView(views.APIView):
    """Public endpoint: GET /api/store/<slug>/info/"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        try:
            company = Company.objects.get(slug=slug, is_active=True)
        except Company.DoesNotExist:
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyPublicSerializer(company)
        return Response(serializer.data)
>>>>>>> dev
