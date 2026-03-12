from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()   # for reading (full URL)
    image     = serializers.ImageField(required=False, allow_null=True, write_only=False)  # for writing

    class Meta:
        model  = Product
        fields = ['id', 'store', 'name', 'description', 'price', 'stock', 'is_active', 'image', 'image_url']

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return f'http://127.0.0.1:8000{obj.image.url}'