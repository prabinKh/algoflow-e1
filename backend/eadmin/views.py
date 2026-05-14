from rest_framework import viewsets, permissions, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import UserActivity, POSSale, ServiceTicket, ContactMessage, CategoryFeature, ChatSession, ChatMessage, StaffRole, StaffMember
from efrontend.models import Product, Order, Category, Brand
from account.models import User
from .serializers import (
    UserActivitySerializer, AdminProductSerializer, AdminOrderSerializer,
    CustomerSerializer, POSSaleSerializer, ServiceTicketSerializer,
    ContactMessageSerializer, CategoryFeatureSerializer,
    ChatSessionSerializer, ChatMessageSerializer,
    StaffRoleSerializer, StaffMemberSerializer, AdminBrandSerializer,
)
from .tasks import generate_ai_response
from efrontend.serializers import HeroSettingSerializer, CategorySerializer

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_admin or request.user.is_staff or request.user.is_superuser
        )


class DashboardStatsView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        total_sales = Order.objects.filter(status='delivered').aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0
        this_month_sales = Order.objects.filter(
            status='delivered', created_at__gte=month_start
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        last_month_sales = Order.objects.filter(
            status='delivered', created_at__gte=last_month_start, created_at__lt=month_start
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        total_customers = User.objects.filter(is_admin=False, is_staff=False).count()
        low_stock_products = Product.objects.filter(stock__lt=10).count()
        total_products = Product.objects.count()

        # Recent orders
        recent_orders = Order.objects.order_by('-created_at')[:5]
        recent_orders_data = [{
            'id': o.id,
            'orderId': o.order_id,
            'customerName': o.full_name,
            'customerEmail': o.email,
            'totalAmount': float(o.total_amount),
            'status': o.status,
            'createdAt': o.created_at.isoformat(),
        } for o in recent_orders]

        # Monthly revenue chart (last 7 months)
        monthly_revenue = []
        for i in range(6, -1, -1):
            m_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1, hour=0, minute=0, second=0)
            m_end = (m_start + timedelta(days=32)).replace(day=1)
            rev = Order.objects.filter(
                status='delivered', created_at__gte=m_start, created_at__lt=m_end
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            monthly_revenue.append({
                'month': m_start.strftime('%b %Y'),
                'revenue': float(rev),
            })

        # Top products by sales
        top_products = (
            Order.objects.filter(status='delivered')
            .values('items__product__id', 'items__product__name', 'items__name')
            .annotate(total_qty=Sum('items__quantity'), total_rev=Sum('items__price'))
            .order_by('-total_qty')[:5]
        )

        sales_growth = 0
        if last_month_sales:
            sales_growth = round(((float(this_month_sales) - float(last_month_sales)) / float(last_month_sales)) * 100, 1)

        return Response({
            'total_sales': float(total_sales),
            'this_month_sales': float(this_month_sales),
            'sales_growth': sales_growth,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_customers': total_customers,
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'recent_orders': recent_orders_data,
            'monthly_revenue': monthly_revenue,
            'top_products': list(top_products),
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdminProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category').order_by('-created_at')
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(brand__name__icontains=search) | Q(brand_name__icontains=search))
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        return qs


class AdminOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items').order_by('-created_at')
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Map camelCase to snake_case for updates
        data = request.data.copy()
        if 'paymentStatus' in data:
            data['payment_status'] = data.pop('paymentStatus')
        if 'paymentMethod' in data:
            data['payment_method'] = data.pop('paymentMethod')
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Direct model update for unmapped fields
        if 'payment_status' in data:
            instance.payment_status = data['payment_status']
        if 'status' in data:
            instance.status = data['status']
        instance.save()
        return Response(AdminOrderSerializer(instance).data)


class CustomerListView(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_admin=False, is_staff=False, is_superuser=False).annotate(
        order_count=Count('order'),
        total_spent=Sum('order__total_amount')
    )
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'sync_cart', 'sync_wishlist']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    def get_object(self):
        pk = self.kwargs.get('pk')
        email = self.request.query_params.get('email') or ''

        # 1. Try UUID primary key (MyUser uses UUID pk)
        try:
            import uuid as _uuid
            uid_val = _uuid.UUID(str(pk))
            user = User.objects.get(id=uid_val)
            return user
        except (ValueError, User.DoesNotExist):
            pass

        # 2. Try firebase_uid string match
        try:
            user = User.objects.get(firebase_uid=pk)
            return user
        except User.DoesNotExist:
            pass

        # 3. Try email lookup
        if email:
            try:
                user = User.objects.get(email=email)
                return user
            except User.DoesNotExist:
                pass

        # 4. Create a guest user record (safe creation)
        safe_email = email if email and '@' in email else f'guest_{str(pk)[:8]}@guest.local'
        safe_name = email.split('@')[0] if email and '@' in email else 'Guest'
        try:
            user, created = User.objects.get_or_create(
                firebase_uid=str(pk),
                defaults={
                    'email': safe_email,
                    'name': safe_name,
                }
            )
        except Exception:
            # If all else fails, return a 404
            from rest_framework.exceptions import NotFound
            raise NotFound(detail='Customer not found')

        return user

    @action(detail=True, methods=['post'], url_path='sync_cart', permission_classes=[permissions.AllowAny])
    def sync_cart(self, request, pk=None):
        user = self.get_object()
        user.cart_items = request.data.get('cartItems', [])
        user.save(update_fields=['cart_items', 'updated_at'])
        return Response({'success': True, 'cartItems': user.cart_items})

    @action(detail=True, methods=['post'], url_path='sync_wishlist', permission_classes=[permissions.AllowAny])
    def sync_wishlist(self, request, pk=None):
        user = self.get_object()
        user.wishlist_items = request.data.get('wishlistItems', [])
        user.save(update_fields=['wishlist_items', 'updated_at'])
        return Response({'success': True, 'wishlistItems': user.wishlist_items})


@method_decorator(csrf_exempt, name='dispatch')
class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = UserActivity.objects.all().order_by('-timestamp')
    serializer_class = UserActivitySerializer

    def get_authenticators(self):
        if getattr(self, 'action', None) == 'create':
            return []
        return super().get_authenticators()

    def get_permissions(self):
        action = getattr(self, 'action', None)
        if action == 'create':
            return [permissions.AllowAny()]
        if action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = UserActivity.objects.all().order_by('-timestamp')
        if self.request.user.is_authenticated and not (
            self.request.user.is_admin or self.request.user.is_staff
        ):
            return queryset.filter(user=self.request.user)
        uid = self.request.query_params.get('uid')
        if uid:
            # Safe filter: firebase_uid is a string, id is UUID — don't mix types
            try:
                import uuid as _uuid
                uid_as_uuid = _uuid.UUID(str(uid))
                queryset = queryset.filter(Q(user__firebase_uid=uid) | Q(user__id=uid_as_uuid))
            except ValueError:
                queryset = queryset.filter(user__firebase_uid=uid)
        return queryset


class POSSaleViewSet(viewsets.ModelViewSet):
    queryset = POSSale.objects.all()
    serializer_class = POSSaleSerializer
    permission_classes = [IsAdminUser]


@method_decorator(csrf_exempt, name='dispatch')
class AdminServiceTicketViewSet(viewsets.ModelViewSet):
    queryset = ServiceTicket.objects.all().order_by('-created_at')
    serializer_class = ServiceTicketSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = ServiceTicket.objects.all().order_by('-created_at')
        if self.request.user.is_authenticated and not (
            self.request.user.is_admin or self.request.user.is_staff
        ):
            return queryset.filter(user=self.request.user)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(
                Q(user__firebase_uid=user_id) | Q(user__id=user_id)
            )
        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        # Try to find user by uid in request data
        uid = self.request.data.get('userId') or self.request.data.get('user_id')
        if uid and not user:
            user = User.objects.filter(Q(firebase_uid=uid) | Q(id=uid)).first()
        serializer.save(user=user)


class AdminContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdminUser]


@method_decorator(csrf_exempt, name='dispatch')
class AdminCategoryFeatureViewSet(viewsets.ModelViewSet):
    """
    Returns features grouped by category slug, matching frontend format:
    { id, categorySlug, categoryName, features: [] }
    """
    queryset = CategoryFeature.objects.all().select_related('category')
    serializer_class = CategoryFeatureSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    def list(self, request, *args, **kwargs):
        """Return grouped format by categorySlug"""
        features = CategoryFeature.objects.filter(is_active=True).select_related('category')
        grouped = {}
        for f in features:
            slug = f.category.slug
            if slug not in grouped:
                grouped[slug] = {
                    'id': slug,
                    'categorySlug': slug,
                    'categoryName': f.category.name,
                    'features': []
                }
            grouped[slug]['features'].append(f.feature_name)
        return Response(list(grouped.values()))

    def create(self, request, *args, **kwargs):
        """
        Accept { categorySlug, categoryName, features: [] } or individual feature
        """
        data = request.data
        category_slug = data.get('categorySlug') or data.get('category_slug') or data.get('categoryName', '').lower().replace(' ', '-')
        features_list = data.get('features', [])
        category_name = data.get('categoryName') or category_slug

        cat = Category.objects.filter(slug=category_slug).first()
        if not cat:
            cat = Category.objects.create(name=category_name, slug=category_slug)

        if 'features' in data:
            features_list = data.get('features', [])
            # Bulk create/update
            existing = list(CategoryFeature.objects.filter(category=cat).values_list('feature_name', flat=True))
            for feature_name in features_list:
                if feature_name not in existing:
                    CategoryFeature.objects.create(category=cat, feature_name=feature_name)
            # Actually delete removed ones instead of just making them inactive
            CategoryFeature.objects.filter(
                category=cat
            ).exclude(feature_name__in=features_list).delete()
            return Response({
                'id': category_slug,
                'categorySlug': category_slug,
                'categoryName': category_name,
                'features': features_list
            }, status=status.HTTP_201_CREATED)
        else:
            # Single feature
            feature_name = data.get('feature_name') or data.get('featureName', '')
            if not feature_name:
                return Response({'error': 'feature_name required'}, status=400)
            obj, created = CategoryFeature.objects.get_or_create(category=cat, feature_name=feature_name)
            return Response(CategoryFeatureSerializer(obj).data, status=status.HTTP_201_CREATED if created else 200)

    @action(detail=False, methods=['post', 'put'], url_path='update-features')
    def update_features(self, request):
        """PATCH grouped features for a category"""
        return self.create(request)


@method_decorator(csrf_exempt, name='dispatch')
class AdminCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]


@method_decorator(csrf_exempt, name='dispatch')
class AdminBrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by('name')
    serializer_class = AdminBrandSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]


class UploadView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        f = request.FILES.get('file')
        if not f:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        folder = request.data.get('path', 'uploads')
        save_path = default_storage.save(f"{folder}/{f.name}", ContentFile(f.read()))
        url = request.build_absolute_uri(f"/media/{save_path}")
        return Response({'url': url})


class UploadModelView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        f = request.FILES.get('file')
        if not f:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        save_path = default_storage.save(f"models/{f.name}", ContentFile(f.read()))
        url = request.build_absolute_uri(f"/media/{save_path}")
        return Response({'url': url})


@method_decorator(csrf_exempt, name='dispatch')
class AdminHeroSettingViewSet(viewsets.ModelViewSet):
    queryset = __import__('efrontend.models', fromlist=['HeroSetting']).HeroSetting.objects.all().order_by('order')
    serializer_class = HeroSettingSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        HeroSetting = __import__('efrontend.models', fromlist=['HeroSetting']).HeroSetting
        existing = HeroSetting.objects.first()
        
        data = request.data.copy()
        if 'description' in data and 'subtitle' not in data:
            data['subtitle'] = data['description']
            
        if existing:
            serializer = self.get_serializer(existing, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all().order_by('-last_message_time')
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.is_staff
        ):
            return ChatSession.objects.all().order_by('-last_message_time')
        if self.request.user.is_authenticated:
            return ChatSession.objects.filter(user=self.request.user).order_by('-last_message_time')
        guest_id = self.request.query_params.get('guest_id')
        if guest_id:
            return ChatSession.objects.filter(user_id_str=guest_id).order_by('-last_message_time')
        return ChatSession.objects.none()

    def perform_update(self, serializer):
        instance = serializer.save()
        if self.request.data.get('unreadAdminCount') == 0 or self.request.data.get('unread_admin_count') == 0:
            instance.unread_admin_count = 0
            instance.save(update_fields=['unread_admin_count', 'updated_at'])
        if self.request.data.get('unreadUserCount') == 0 or self.request.data.get('unread_user_count') == 0:
            instance.unread_user_count = 0
            instance.save(update_fields=['unread_user_count', 'updated_at'])


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        if session_id:
            return ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
        return ChatMessage.objects.none()

    def perform_create(self, serializer):
        message = serializer.save()
        session = message.session

        session.last_message = message.text
        if message.sender == 'user':
            session.unread_admin_count = (session.unread_admin_count or 0) + 1
        else:
            session.unread_user_count = (session.unread_user_count or 0) + 1
        session.save(update_fields=['last_message', 'unread_admin_count', 'unread_user_count', 'last_message_time', 'updated_at'])

        if message.sender == 'user':
            try:
                generate_ai_response.delay(message.session.id, message.text)
            except Exception as e:
                print(f"AI task failed: {e}")


class ReportsView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        report_type = request.query_params.get('type', 'sales')

        if report_type == 'sales_by_category':
            data = list(Order.objects.filter(status='delivered').values(
                'items__product__category__name'
            ).annotate(
                total_sales=Sum('items__price'),
                total_orders=Count('id', distinct=True)
            ))
        elif report_type == 'sales_by_brand':
            data = list(Order.objects.filter(status='delivered').values(
                'items__product__brand'
            ).annotate(
                total_sales=Sum('items__price'),
                total_orders=Count('id', distinct=True)
            ))
        elif report_type == 'sales_by_product':
            data = list(Order.objects.filter(status='delivered').values(
                'items__product__name', 'items__name'
            ).annotate(
                total_sales=Sum('items__price'),
                total_quantity=Sum('items__quantity'),
                total_orders=Count('id', distinct=True)
            ).order_by('-total_sales')[:20])
        elif report_type == 'sales_by_status':
            data = list(Order.objects.values('status').annotate(count=Count('id')))
        elif report_type == 'stock_report':
            data = list(Product.objects.values('name', 'brand', 'stock', 'category__name').order_by('stock'))
        elif report_type == 'customer_stats':
            data = User.objects.filter(is_admin=False).aggregate(
                total_customers=Count('id'),
                avg_spent=Sum('order__total_amount')
            )
        else:
            data = {'error': 'Invalid report type'}

        return Response(data)

class StaffRoleViewSet(viewsets.ModelViewSet):
    queryset = StaffRole.objects.all()
    serializer_class = StaffRoleSerializer
    permission_classes = [IsAdminUser]

class StaffMemberViewSet(viewsets.ModelViewSet):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        role_id = self.request.query_params.get('role')
        if role_id:
            qs = qs.filter(role_id=role_id)
        return qs
