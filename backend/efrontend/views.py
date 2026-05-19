from rest_framework import generics, permissions, filters, views, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Product, Order, OrderItem, HeroSetting, Wishlist, Review, StoreLocation, AIRecommendation
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, OrderSerializer,
    HeroSettingSerializer, WishlistSerializer, ReviewSerializer,
    StoreLocationSerializer, AIRecommendationSerializer
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'


class BrandListView(generics.ListCreateAPIView):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)
        return queryset.distinct()


class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'brand', 'is_new', 'is_best_seller', 'in_stock']
    search_fields = ['name', 'brand', 'description']
    ordering_fields = ['price', 'created_at', 'rating']

    def get_queryset(self):
<<<<<<< HEAD
=======
        from company.models import Company
>>>>>>> dev
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
            
<<<<<<< HEAD
        company = self.request.query_params.get('company')
        if company:
            queryset = queryset.filter(company__slug=company)
=======
        company_obj = Company.resolve_from_request(self.request)
        if company_obj:
            queryset = queryset.filter(company=company_obj)
>>>>>>> dev
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'


class HeroSettingView(generics.ListAPIView):
    serializer_class = HeroSettingSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
<<<<<<< HEAD
        qs = HeroSetting.objects.filter(is_active=True).order_by('order')
        company = self.request.query_params.get('company')
        if company:
            qs = qs.filter(company__slug=company)
        else:
            qs = qs.filter(company__isnull=True)
=======
        from company.models import Company
        qs = HeroSetting.objects.filter(is_active=True).order_by('order')
        company_obj = Company.resolve_from_request(self.request)
        if company_obj:
            qs = qs.filter(company=company_obj)
>>>>>>> dev
        return qs


class OrderCreateView(views.APIView):
    """
    Accept frontend order format:
    {
      uid, items: [{productId, name, price, quantity, image, features}],
      totalAmount, subtotal, tax, discount,
      shippingAddress: {address, city, phone},
      customerName, customerEmail, status, paymentStatus, paymentMethod,
      source, orderId, customerType
    }
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = request.data
        shipping = data.get('shippingAddress') or {}
        items = data.get('items') or []
        if not items:
            return Response({'error': 'Order items are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        uid = data.get('uid') or ''
        if uid and request.user.is_authenticated:
            user = request.user
        elif request.user.is_authenticated:
            user = request.user

        # Group items by company
        company_items_map = {}
        for item in items:
            product_id = item.get('productId') or item.get('product_id')
            product = None
            company = None
            if product_id:
                try:
                    from django.db.models import Q
                    product = Product.objects.filter(Q(id=product_id) | Q(slug=product_id)).first()
                    if product and product.company:
                        company = product.company
                except Exception:
                    pass
            
<<<<<<< HEAD
            item['_product'] = product
            company_id = company.id if company else None
=======
            # Fallback to the authenticated user's company (for POS/Admin)
            if not company and request.user.is_authenticated:
                if hasattr(request.user, 'company') and request.user.company:
                    company = request.user.company

            if not company:
                return Response({'error': f'Could not determine company for product ID: {product_id}'}, status=status.HTTP_400_BAD_REQUEST)
            
            item['_product'] = product
            company_id = company.id
>>>>>>> dev
            if company_id not in company_items_map:
                company_items_map[company_id] = {
                    'company': company,
                    'items': [],
                    'subtotal': 0
                }
            
            company_items_map[company_id]['items'].append(item)
            company_items_map[company_id]['subtotal'] += float(item.get('price', 0)) * int(item.get('quantity', 1))

        created_orders = []
        base_order_id = data.get('orderId', '')
        
        for idx, (comp_id, group) in enumerate(company_items_map.items()):
            subtotal = group['subtotal']
            
            # If split order, suffix the ID
            order_id = f"{base_order_id}-{idx+1}" if len(company_items_map) > 1 and base_order_id else base_order_id
            
            order = Order.objects.create(
                user=user,
                company=group['company'],
                uid=uid,
                order_id=order_id,
                email=data.get('customerEmail', ''),
                full_name=data.get('customerName', ''),
                address=shipping.get('address', ''),
                city=shipping.get('city', ''),
                phone=shipping.get('phone', ''),
                subtotal=subtotal,
                tax=0,  # simplified for split
                discount=0, # simplified for split
                total_amount=subtotal, # simplified
                status=data.get('status', 'pending'),
                payment_status=data.get('paymentStatus', 'unpaid'),
                payment_method=data.get('paymentMethod', 'cash'),
                source=data.get('source', 'store'),
                customer_type=data.get('customerType', 'registered'),
            )
            created_orders.append(order)
            
            for item in group['items']:
                product = item['_product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_id_str=str(product.id) if product else str(item.get('productId', '')),
                    name=item.get('name', product.name if product else ''),
                    image=item.get('image', product.image if product else ''),
                    features=item.get('features', []),
                    quantity=item.get('quantity', 1),
                    price=item.get('price', 0),
                )

        # Return the first order data for frontend compatibility
        return Response(OrderSerializer(created_orders[0]).data, status=status.HTTP_201_CREATED)


class OrderTrackView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        pk = self.kwargs.get('id')
        try:
            return Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Order.objects.get(order_id=pk)


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class WishlistViewSet(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        wishlist = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist_item.delete()
            return Response({'status': 'removed'})
        return Response({'status': 'added'})


class ReviewViewSet(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        data = request.data.copy()
        data['product'] = product_id
        data['user'] = request.user.id
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreLocationView(generics.ListAPIView):
    serializer_class = StoreLocationSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
<<<<<<< HEAD
        qs = StoreLocation.objects.all()
        company = self.request.query_params.get('company')
        if company:
            qs = qs.filter(company__slug=company)
=======
        from company.models import Company
        qs = StoreLocation.objects.all()
        company_obj = Company.resolve_from_request(self.request)
        if company_obj:
            qs = qs.filter(company=company_obj)
>>>>>>> dev
        return qs


class AIRecommendationView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        query = request.data.get('query', '')
        products = Product.objects.all()[:20]
        product_list = [{'name': p.name, 'brand': p.brand, 'price': float(p.price), 'category': p.category.name} for p in products]
        rec = AIRecommendation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=query,
            recommendations=product_list[:5],
            reasoning='Based on available products'
        )
        from .serializers import AIRecommendationSerializer
        return Response(AIRecommendationSerializer(rec).data)
<<<<<<< HEAD
=======


class CurrentCompanyView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        from company.models import Company
        from company.serializers import CompanyPublicSerializer
        company = Company.resolve_from_request(request)
        if company:
            return Response(CompanyPublicSerializer(company).data)
        return Response({'detail': 'No company active'}, status=status.HTTP_404_NOT_FOUND)
>>>>>>> dev
