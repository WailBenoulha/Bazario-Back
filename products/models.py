from django.db import models
from stores.models import Store

class ProductImage(models.Model):
    product    = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='images'
    )
    image      = models.ImageField(upload_to='product_images/')
    is_primary = models.BooleanField(default=False)
    order      = models.PositiveIntegerField(default=0)
 
    class Meta:
        ordering = ['-is_primary', 'order', 'id']
 
    def __str__(self):
        return f"Image for {self.product.name} (primary={self.is_primary})"
 
 
class ProductSize(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='sizes')
    label   = models.CharField(max_length=20)   # "S", "M", "XL", "250ml"
    stock   = models.PositiveIntegerField(default=0)
 
    class Meta:
        ordering = ['id']
 
 
class ProductColor(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='colors')
    name    = models.CharField(max_length=50)    # "Ocean Blue"
    hex     = models.CharField(max_length=10)    # "#0066cc"
 
    class Meta:
        ordering = ['id']

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    brand       = models.CharField(max_length=100, blank=True, default='')
    material    = models.CharField(max_length=200, blank=True, default='')
    weight      = models.CharField(max_length=50,  blank=True, default='')

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock <= 5