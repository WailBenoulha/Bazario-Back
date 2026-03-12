from rest_framework import serializers
from .models import Store
 
 
class StoreSerializer(serializers.ModelSerializer):
    # logo_url returns the full URL to the uploaded logo image
    logo_url = serializers.SerializerMethodField()
 
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'slug', 'niche', 'description',
            'is_live', 'plan',
            # ↓ THESE THREE MUST BE HERE — this is what the storefront reads
            'accent_color', 'button_style', 'panel_style',
            'logo', 'logo_url',
        ]
 
    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        if obj.logo:
            return obj.logo.url
        return None