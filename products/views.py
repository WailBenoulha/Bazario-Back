from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer
 
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class ProductViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, JSONParser]  
    serializer_class = ProductSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['store', 'is_active']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.filter(is_active=True)
        return Product.objects.filter(store__owner=user)