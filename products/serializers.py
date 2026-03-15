from rest_framework import serializers
from .models import Product,ProductImage,ProductColor,ProductSize

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
 
    class Meta:
        model  = ProductImage
        fields = ['id', 'product', 'image', 'image_url', 'is_primary', 'order']
        extra_kwargs = {'image': {'write_only': False}}
 
    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return f'http://127.0.0.1:8000{obj.image.url}'
    
class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductSize
        fields = ['id', 'label', 'stock']
 
 
class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductColor
        fields = ['id', 'name', 'hex']    

class ProductSerializer(serializers.ModelSerializer):
    # ── Read-only computed fields ──
    image_url   = serializers.SerializerMethodField()
    images      = ProductImageSerializer(many=True, read_only=True)  # ← KEY FIELD
    sizes       = ProductSizeSerializer(many=True, read_only=True)
    colors      = ProductColorSerializer(many=True, read_only=True)
    # ── Write-only JSON fields from React ──
    sizes_data  = serializers.CharField(write_only=True, required=False, allow_blank=True)
    colors_data = serializers.CharField(write_only=True, required=False, allow_blank=True)
 
    class Meta:
        model  = Product
        fields = [
            'id', 'store', 'name', 'description', 'price', 'stock', 'is_active',
            'image', 'image_url',
            'images',           # ← must be here
            'sizes', 'colors',
            'brand', 'material', 'weight',
            'sizes_data', 'colors_data',
        ]
 
    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return f'http://127.0.0.1:8000{obj.image.url}'
 
    def create(self, validated_data):
        sizes_data  = validated_data.pop('sizes_data',  None)
        colors_data = validated_data.pop('colors_data', None)
        product = super().create(validated_data)
        self._save_variants(product, sizes_data, colors_data)
        # Auto-create a ProductImage record for the primary image
        if product.image:
            ProductImage.objects.get_or_create(
                product=product, is_primary=True,
                defaults={'image': product.image, 'order': 0}
            )
        return product
 
    def update(self, instance, validated_data):
        sizes_data  = validated_data.pop('sizes_data',  None)
        colors_data = validated_data.pop('colors_data', None)
        old_image = str(instance.image) if instance.image else None
        product = super().update(instance, validated_data)
        self._save_variants(product, sizes_data, colors_data)
        # Sync primary ProductImage record when image changed
        new_image = str(product.image) if product.image else None
        if product.image and new_image != old_image:
            primary = product.images.filter(is_primary=True).first()
            if primary:
                primary.image = product.image
                primary.save(update_fields=['image'])
            else:
                ProductImage.objects.create(
                    product=product, image=product.image, is_primary=True, order=0
                )
        return product
 
    def _save_variants(self, product, sizes_data, colors_data):
        import json
        if sizes_data:
            try:
                product.sizes.all().delete()
                for i, s in enumerate(json.loads(sizes_data)):
                    ProductSize.objects.create(
                        product=product, label=s['label'], stock=int(s.get('stock', 0))
                    )
            except Exception as e:
                pass
        if colors_data:
            try:
                product.colors.all().delete()
                for c in json.loads(colors_data):
                    ProductColor.objects.create(
                        product=product, name=c['name'], hex=c.get('hex', '#000000')
                    )
            except Exception as e:
                pass