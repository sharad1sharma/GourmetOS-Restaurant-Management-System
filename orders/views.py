from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    Orders are created in 'pending' status with their line items.

    Lifecycle endpoints:
    - POST /api/orders/{id}/confirm/   -> validates & deducts inventory, status -> confirmed
    - POST /api/orders/{id}/advance/   -> body: {"status": "preparing"|"ready"|"served"}
    - POST /api/orders/{id}/complete/  -> marks paid/completed, frees table for cleaning
    - POST /api/orders/{id}/cancel/    -> cancels, restocks inventory if it was deducted
    """
    queryset = Order.objects.select_related('table').prefetch_related('items__menu_item')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'order_type', 'table']
    ordering_fields = ['created_at', 'updated_at']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        try:
            order.confirm()
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def advance(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        valid_next = {'confirmed': 'preparing', 'preparing': 'ready', 'ready': 'served'}
        if new_status not in ('preparing', 'ready', 'served'):
            return Response({"detail": "status must be one of: preparing, ready, served"},
                             status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        order = self.get_object()
        try:
            order.mark_completed()
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        try:
            order.cancel()
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)
