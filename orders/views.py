from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'store']
    search_fields = ['customer_name', 'customer_email', 'id']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']

    def get_permissions(self):
        # Anyone can create an order (buyers checking out)
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Order.objects.filter(store__owner=self.request.user).prefetch_related('items')

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=400)
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        qs = self.get_queryset()
        return Response({
            'total_orders': qs.count(),
            'total_revenue': sum(o.total for o in qs.filter(status='delivered')),
            'pending': qs.filter(status='pending').count(),
            'processing': qs.filter(status='processing').count(),
            'delivered': qs.filter(status='delivered').count(),
            'cancelled': qs.filter(status='cancelled').count(),
        })