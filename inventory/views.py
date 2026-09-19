from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import InventoryItem, StockMovement
from .serializers import InventoryItemSerializer, RestockSerializer, StockMovementSerializer


class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    CRUD for inventory items, plus:
    - GET  /api/inventory/low-stock/      -> items at/below reorder level
    - POST /api/inventory/{id}/restock/   -> add stock, body: {"amount": 10}
    """
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['unit']
    search_fields = ['name']
    ordering_fields = ['name', 'quantity_in_stock', 'reorder_level']

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        low_items = [item for item in self.get_queryset() if item.is_low_stock]
        serializer = self.get_serializer(low_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restock(self, request, pk=None):
        item = self.get_object()
        serializer = RestockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        item.restock(amount)
        StockMovement.objects.create(
            item=item, change=amount, reason='restock', reference='Manual restock via API'
        )
        return Response(InventoryItemSerializer(item).data, status=status.HTTP_200_OK)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.select_related('item').all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['item', 'reason']
