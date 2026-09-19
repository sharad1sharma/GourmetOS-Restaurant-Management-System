from decimal import Decimal

from rest_framework import serializers
from .models import InventoryItem, StockMovement


class InventoryItemSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'unit', 'quantity_in_stock', 'reorder_level',
            'cost_per_unit', 'is_low_stock', 'last_restocked_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['last_restocked_at', 'created_at', 'updated_at']


class RestockSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))


class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id', 'item', 'item_name', 'change', 'reason', 'reference', 'created_at']
        read_only_fields = ['created_at']
