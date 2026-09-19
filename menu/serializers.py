from rest_framework import serializers
from .models import Category, MenuItem, RecipeItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class RecipeItemSerializer(serializers.ModelSerializer):
    inventory_item_name = serializers.CharField(source='inventory_item.name', read_only=True)
    unit = serializers.CharField(source='inventory_item.unit', read_only=True)

    class Meta:
        model = RecipeItem
        fields = ['id', 'menu_item', 'inventory_item', 'inventory_item_name', 'unit', 'quantity_required']


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_orderable = serializers.BooleanField(read_only=True)
    recipe_items = RecipeItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'category', 'category_name', 'price',
            'is_available', 'is_vegetarian', 'image_url', 'prep_time_minutes',
            'is_in_stock', 'is_orderable', 'recipe_items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
