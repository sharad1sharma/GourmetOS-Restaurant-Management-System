from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Sum, Count, F
from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from orders.models import Order, OrderItem
from inventory.models import InventoryItem


class DailySalesReportView(APIView):
    """
    GET /api/reports/daily-sales/?date=YYYY-MM-DD
    Defaults to today. Reports on completed orders only.
    """

    def get(self, request):
        date_str = request.query_params.get('date')
        target_date = parse_date(date_str) if date_str else timezone.localdate()
        if target_date is None:
            return Response({"detail": "Invalid 'date' format, use YYYY-MM-DD."}, status=400)

        start = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
        end = start + timedelta(days=1)

        orders = Order.objects.filter(
            status='completed', completed_at__gte=start, completed_at__lt=end
        )

        total_orders = orders.count()
        total_revenue = sum((o.total_amount for o in orders), Decimal('0.00'))

        top_items = (
            OrderItem.objects.filter(order__in=orders)
            .values('menu_item__name')
            .annotate(
                quantity_sold=Sum('quantity'),
                revenue=Sum(F('unit_price') * F('quantity')),
            )
            .order_by('-quantity_sold')[:10]
        )

        by_type = orders.values('order_type').annotate(count=Count('id'))

        return Response({
            "date": str(target_date),
            "total_orders": total_orders,
            "total_revenue": str(total_revenue),
            "orders_by_type": list(by_type),
            "top_selling_items": list(top_items),
        })


class StockAlertsReportView(APIView):
    """GET /api/reports/stock-alerts/ -> inventory items at/below reorder level."""

    def get(self, request):
        low_items = [item for item in InventoryItem.objects.all() if item.is_low_stock]
        data = [
            {
                "id": item.id,
                "name": item.name,
                "quantity_in_stock": str(item.quantity_in_stock),
                "reorder_level": str(item.reorder_level),
                "unit": item.unit,
            }
            for item in low_items
        ]
        return Response({"count": len(data), "low_stock_items": data})
