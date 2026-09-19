from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, MenuItem, RecipeItem
from .serializers import CategorySerializer, MenuItemSerializer, RecipeItemSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    CRUD for menu items. Supports:
    - ?category=<id>
    - ?is_vegetarian=true
    - ?search=<name>

    Plus GET /api/menu-items/orderable/ -> only items that are toggled
    available AND have enough ingredient stock right now.
    """
    queryset = MenuItem.objects.select_related('category').prefetch_related('recipe_items__inventory_item')
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_vegetarian', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'prep_time_minutes']

    @action(detail=False, methods=['get'])
    def orderable(self, request):
        orderable_items = [item for item in self.filter_queryset(self.get_queryset()) if item.is_orderable]
        serializer = self.get_serializer(orderable_items, many=True)
        return Response(serializer.data)


class RecipeItemViewSet(viewsets.ModelViewSet):
    queryset = RecipeItem.objects.select_related('menu_item', 'inventory_item').all()
    serializer_class = RecipeItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['menu_item', 'inventory_item']
