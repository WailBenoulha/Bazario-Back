# app/urls.py  — REPLACE your current file with this

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Import ProductImageViewSet from your products app
from products.views import ProductImageViewSet

# Root-level router — only for viewsets that don't belong to a single app router
router = DefaultRouter()
router.register(r'product-images', ProductImageViewSet, basename='product-images')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),          # ← gives /api/product-images/
    path('api/auth/',     include('accounts.urls')),
    path('api/stores/',   include('stores.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/',   include('orders.urls')),
    path('api/plans/',    include('plans.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# This gives you these working URLs:
#
#   POST   /api/product-images/              ← upload new image
#   GET    /api/product-images/?product=<id> ← list images for a product
#   DELETE /api/product-images/<id>/         ← delete one image
#
# Your existing URLs are completely unchanged.