from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductImageSerializer, ProductSerializer,ProductImage
 
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


    

from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
 
class ProductImageViewSet(viewsets.ModelViewSet):
    """
    Handles individual product image uploads and deletions.
 
    POST   /api/product-images/        — upload new image
    GET    /api/product-images/?product=<id>  — list images for product
    DELETE /api/product-images/<id>/   — delete an image
    """
    serializer_class = ProductImageSerializer
    parser_classes   = [MultiPartParser, FormParser]
 
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
 
    def get_queryset(self):
        qs = ProductImage.objects.select_related('product__store')
        # Optional filter by product id
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product__id=product_id)
        user = self.request.user
        if user.is_authenticated:
            return qs.filter(product__store__owner=user)
        return qs.filter(product__is_active=True, product__store__is_live=True)
 
    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        # Set order to next available slot
        order = ProductImage.objects.filter(product=product).count()
        # If no primary exists yet, make this one primary
        has_primary = ProductImage.objects.filter(product=product, is_primary=True).exists()
        is_primary  = not has_primary
        serializer.save(is_primary=is_primary, order=order)



class ProductViewSet(viewsets.ModelViewSet):
    parser_classes   = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ProductSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['store', 'is_active']
 
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
 
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.filter(
                is_active=True
            ).prefetch_related('images', 'sizes', 'colors')   # ← prefetch images
        return Product.objects.filter(
            store__owner=user
        ).prefetch_related('images', 'sizes', 'colors')       # ← prefetch images        