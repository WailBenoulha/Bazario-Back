from rest_framework import serializers
from .models import Product, ProductImage, ProductColor, ProductSize
from stores.models import Category

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
    image_url      = serializers.SerializerMethodField()
    images         = ProductImageSerializer(many=True, read_only=True)
    sizes          = ProductSizeSerializer(many=True, read_only=True)
    colors         = ProductColorSerializer(many=True, read_only=True)
    sizes_data     = serializers.CharField(write_only=True, required=False, allow_blank=True)
    colors_data    = serializers.CharField(write_only=True, required=False, allow_blank=True)
    categories_data = serializers.CharField(write_only=True, required=False, allow_blank=True)  # ← NEW
 
    # Read-only: list of category IDs
    categories     = serializers.SerializerMethodField()        # ← NEW
 
    # Read-only: list of "icon name" strings for display
    category_names = serializers.SerializerMethodField()        # ← NEW
 
    class Meta:
        model  = Product
        fields = [
            'id', 'store', 'name', 'description', 'price', 'stock', 'is_active',
            'image', 'image_url', 'images',
            'sizes', 'colors',
            'brand', 'material', 'weight',
            'sizes_data', 'colors_data',
            'categories',       # ← NEW: list of IDs [1, 3]
            'category_names',   # ← NEW: list of names ["Smartphones", "Tablets"]
            'categories_data',  # ← NEW: write-only JSON "[1,3]"
        ]
 
    def get_image_url(self, obj):
        if not obj.image: return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else f'http://127.0.0.1:8000{obj.image.url}'
 
    def get_categories(self, obj):
        return list(obj.categories.values_list('id', flat=True))
 
    def get_category_names(self, obj):
        return list(obj.categories.values_list('name', flat=True))
 
    def create(self, validated_data):
        sizes_data      = validated_data.pop('sizes_data', None)
        colors_data     = validated_data.pop('colors_data', None)
        categories_data = validated_data.pop('categories_data', None)
        product = super().create(validated_data)
        self._save_variants(product, sizes_data, colors_data)
        self._save_categories(product, categories_data)
        if product.image:
            ProductImage.objects.get_or_create(
                product=product, is_primary=True,
                defaults={'image': product.image, 'order': 0}
            )
        return product
 
    def update(self, instance, validated_data):
        sizes_data      = validated_data.pop('sizes_data', None)
        colors_data     = validated_data.pop('colors_data', None)
        categories_data = validated_data.pop('categories_data', None)
        old_image = str(instance.image) if instance.image else None
        product   = super().update(instance, validated_data)
        self._save_variants(product, sizes_data, colors_data)
        self._save_categories(product, categories_data)
        new_image = str(product.image) if product.image else None
        if product.image and new_image != old_image:
            primary = product.images.filter(is_primary=True).first()
            if primary:
                primary.image = product.image
                primary.save(update_fields=['image'])
            else:
                ProductImage.objects.create(product=product, image=product.image, is_primary=True, order=0)
        return product
 
    def _save_categories(self, product, categories_data):
        import json
        if categories_data is not None:
            try:
                ids = json.loads(categories_data)
                product.categories.set(ids)   # replaces all existing M2M links
            except Exception:
                pass
 
    def _save_variants(self, product, sizes_data, colors_data):
        import json
        if sizes_data:
            try:
                product.sizes.all().delete()
                for s in json.loads(sizes_data):
                    ProductSize.objects.create(product=product, label=s['label'], stock=int(s.get('stock',0)))
            except Exception: pass
        if colors_data:
            try:
                product.colors.all().delete()
                for c in json.loads(colors_data):
                    ProductColor.objects.create(product=product, name=c['name'], hex=c.get('hex','#000000'))
            except Exception: pass