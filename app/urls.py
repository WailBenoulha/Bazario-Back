from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
 
from products.views import ProductImageViewSet
from stores.views import CategoryViewSet          # ← ADD
 
router = DefaultRouter()
router.register(r'product-images', ProductImageViewSet, basename='product-images')
router.register(r'categories',     CategoryViewSet,     basename='categories')   # ← ADD
 
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/',     include('accounts.urls')),
    path('api/stores/',   include('stores.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/',   include('orders.urls')),
    path('api/plans/',    include('plans.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)