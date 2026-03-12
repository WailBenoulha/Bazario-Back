from django.db import models
from django.conf import settings

NICHE_CHOICES = [
    ('fashion', 'Fashion'),
    ('electronics', 'Electronics'),
    ('cosmetics', 'Cosmetics'),
    ('food', 'Food & Drinks'),
    ('accessories', 'Accessories'),
    ('sports', 'Sports'),
    ('education', 'Education'),
    ('other', 'Other'),
]

class Store(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    niche = models.CharField(max_length=20, choices=NICHE_CHOICES, default='other')
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='store_logos/', null=True, blank=True)
    is_live = models.BooleanField(default=False)
    plan = models.ForeignKey('plans.Plan', on_delete=models.SET_NULL, null=True, blank=True)
    accent_color = models.CharField(max_length=20,  default='#E87722')
    button_style = models.CharField(max_length=20,  default='soft')
    panel_style  = models.CharField(max_length=20,  default='dark')
    logo         = models.ImageField(upload_to='store_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_revenue(self):
        return sum(o.total for o in self.orders.filter(status='delivered'))

    @property
    def total_orders(self):
        return self.orders.count()

    @property
    def total_customers(self):
        return self.orders.values('customer_email').distinct().count()