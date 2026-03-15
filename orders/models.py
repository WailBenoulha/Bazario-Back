from django.db import models
from stores.models import Store
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=100)
    customer_family_name = models.CharField(max_length=200, blank=True, default='')
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer_address     = models.TextField(blank=True, default='')                   # NEW
    customer_city        = models.CharField(max_length=100, blank=True, default='')   # NEW
    customer_wilaya      = models.CharField(max_length=100, blank=True, default='')   # NEW
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} — {self.customer_name}"

    def calculate_total(self):
        self.total = sum(item.subtotal for item in self.items.all())
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # snapshot
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    selected_size  = models.CharField(max_length=50, blank=True, default='')   # NEW
    selected_color = models.CharField(max_length=100, blank=True, default='')  # NEW

    @property
    def subtotal(self):
        return self.unit_price * self.quantity