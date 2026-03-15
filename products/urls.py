# products/urls.py  — REPLACE your current file with this
# Remove ProductImageViewSet from here entirely

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet   # ← only ProductViewSet, NOT ProductImageViewSet

router = DefaultRouter()
router.register('', ProductViewSet, basename='product')

urlpatterns = [path('', include(router.urls))]