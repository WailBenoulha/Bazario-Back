from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'unit_price', 'quantity', 'subtotal']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrderItem
        fields = ['product', 'quantity', 'selected_size', 'selected_color']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
 
    class Meta:
        model  = Order
        fields = [
            'store', 'customer_name', 'customer_family_name',
            'customer_email', 'customer_phone',
            'customer_address', 'customer_city', 'customer_wilaya',
            'notes', 'items'
        ]
 
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            product = item['product']
            qty     = item['quantity']
            size    = item.get('selected_size',  '')
            color   = item.get('selected_color', '')
            OrderItem.objects.create(
                order=order, product=product,
                product_name=product.name, unit_price=product.price,
                quantity=qty, selected_size=size, selected_color=color,
            )
            # Decrement size-specific stock if sizes exist
            if size:
                size_obj = product.sizes.filter(label=size).first()
                if size_obj:
                    size_obj.stock = max(0, size_obj.stock - qty)
                    size_obj.save()
            else:
                product.stock = max(0, product.stock - qty)
                product.save(update_fields=['stock'])
        order.calculate_total()
        return order