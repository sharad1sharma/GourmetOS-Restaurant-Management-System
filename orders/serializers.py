from rest_framework import serializers
from django.db import transaction

from .models import Order, OrderItem
from menu.models import MenuItem


class OrderItemInputSerializer(serializers.Serializer):
    """Used only for the nested 'items' list when creating an order."""
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    quantity = serializers.IntegerField(min_value=1)
    special_instructions = serializers.CharField(max_length=255, required=False, allow_blank=True)


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'unit_price',
                  'special_instructions', 'line_total']
        read_only_fields = ['unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_input = OrderItemInputSerializer(many=True, write_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, read_only=True)
    table_number = serializers.IntegerField(source='table.number', read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            'id', 'table', 'table_number', 'order_type', 'status', 'customer_name',
            'customer_phone', 'notes', 'items', 'items_input', 'total_amount', 'total_price',
            'created_at', 'updated_at', 'completed_at',
        ]
        read_only_fields = ['status', 'created_at', 'updated_at', 'completed_at']

    def validate_items_input(self, value):
        if not value:
            raise serializers.ValidationError("An order needs at least one item.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items_input')
        order = Order.objects.create(**validated_data)
        for line in items_data:
            OrderItem.objects.create(
                order=order,
                menu_item=line['menu_item'],
                quantity=line['quantity'],
                unit_price=line['menu_item'].price,
                special_instructions=line.get('special_instructions', ''),
            )
        return order
