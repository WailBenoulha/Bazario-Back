from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Store
from .serializers import StoreSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny,IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

class StoreViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug', 'is_live','niche']
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Public can list/retrieve stores (for storefront)
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    filterset_fields = ['slug', 'owner', 'niche', 'is_live']

    def get_queryset(self):
        user = self.request.user
 
        # Anonymous user (buyer visiting storefront)
        if not user.is_authenticated:
            return Store.objects.filter(is_live=True)
 
        # Authenticated user (seller in dashboard)
        # When a seller is logged in AND hits /stores/?slug=X for their own store
        # (e.g. StoresPage), return only their stores
        return Store.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle_live')
    def toggle_live(self, request, pk=None):
        store = self.get_object()
        store.is_live = not store.is_live
        store.save(update_fields=['is_live'])
        return Response(StoreSerializer(store).data)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        store = self.get_object()
        return Response({
            'total_revenue': store.total_revenue,
            'total_orders': store.total_orders,
            'total_customers': store.total_customers,
            'is_live': store.is_live,
            'plan': store.plan.name if store.plan else 'free',
        })
    


from rest_framework import viewsets, permissions
from .models import Category
from .serializers import CategorySerializer
 
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
 
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
 
    def get_queryset(self):
        qs = Category.objects.all()
        store_id = self.request.query_params.get('store')
        if store_id:
            qs = qs.filter(store__id=store_id)
        user = self.request.user
        if user.is_authenticated:
            return (qs.filter(store__owner=user) | qs.filter(store__is_live=True)).distinct()
        return qs.filter(store__is_live=True)