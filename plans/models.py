from django.db import models

class Plan(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_products = models.IntegerField(default=10)
    max_stores = models.IntegerField(default=1)
    custom_domain = models.BooleanField(default=False)
    analytics = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)

    def __str__(self):
        return self.name