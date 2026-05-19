from django.db import models
from account.models import Company

class TenantMiddleware:
    """
    Middleware to identify and attach the current company (tenant) to the request.
    Identification order:
    1. Authenticated user's company.
    2. X-Company-Slug header (for public storefront APIs).
    3. 'company' query parameter (fallback).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = None
        
        # 1. Authenticated user context
        if request.user.is_authenticated:
            # For Company Admins and Customers, use their assigned company
            if hasattr(request.user, 'company') and request.user.company:
                request.company = request.user.company
        
        # 2. Header/Query context (Public APIs or SuperAdmin switching context)
        if not request.company:
            company_slug = request.headers.get('X-Company-Slug') or request.GET.get('company')
            if company_slug:
                try:
                    request.company = Company.objects.get(slug=company_slug, is_active=True)
                except Company.DoesNotExist:
                    pass
        
        # 3. Host-based context (IP/Domain mapping via username OR slug)
        if not request.company:
            host = request.get_host().split(':')[0]
            
            # Handle subdomains (e.g., samsung.localhost -> samsung)
            if '.localhost' in host:
                host = host.split('.localhost')[0]
            elif '.' in host and not host.replace('.', '').isdigit():
                # If it's a domain like samsung.algoflow.com, take the first part
                host = host.split('.')[0]

            try:
                # Try matching username (IPs) or slug (subdomains)
                request.company = Company.objects.filter(
                    models.Q(username=host) | models.Q(slug=host)
                ).filter(is_active=True).first()
            except Exception:
                pass
                    
        response = self.get_response(request)
        return response
