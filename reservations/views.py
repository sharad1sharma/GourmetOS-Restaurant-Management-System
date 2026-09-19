from datetime import datetime

from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Reservation, DEFAULT_RESERVATION_DURATION_MINUTES
from .serializers import ReservationSerializer
from tables.models import Table


class ReservationViewSet(viewsets.ModelViewSet):
    """
    CRUD for reservations. On create/update, availability (capacity + time
    overlap) is validated in the serializer.

    Extra endpoints:
    - GET  /api/reservations/check-availability/?table=<id>&time=<iso>&duration=90
    - POST /api/reservations/{id}/cancel/
    - POST /api/reservations/{id}/seat/
    """
    queryset = Reservation.objects.select_related('table').all()
    serializer_class = ReservationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['table', 'status']
    ordering_fields = ['reservation_time']

    @action(detail=False, methods=['get'], url_path='check-availability')
    def check_availability(self, request):
        table_id = request.query_params.get('table')
        time_str = request.query_params.get('time')
        duration = int(request.query_params.get('duration', DEFAULT_RESERVATION_DURATION_MINUTES))

        if not table_id or not time_str:
            return Response(
                {"detail": "Both 'table' and 'time' (ISO 8601) query params are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        requested_time = parse_datetime(time_str)
        if requested_time is None:
            return Response({"detail": "Invalid 'time' format, use ISO 8601."},
                             status=status.HTTP_400_BAD_REQUEST)

        try:
            table = Table.objects.get(pk=table_id)
        except Table.DoesNotExist:
            return Response({"detail": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

        clashes = Reservation.objects.filter(table=table, status__in=['confirmed', 'seated'])
        conflicting = [r for r in clashes if r.overlaps(requested_time, duration)]

        return Response({
            "table": table.number,
            "available": len(conflicting) == 0,
            "conflicting_reservations": [
                {"id": r.id, "customer_name": r.customer_name, "reservation_time": r.reservation_time}
                for r in conflicting
            ],
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        reservation.status = 'cancelled'
        reservation.save(update_fields=['status'])
        return Response(ReservationSerializer(reservation).data)

    @action(detail=True, methods=['post'])
    def seat(self, request, pk=None):
        reservation = self.get_object()
        reservation.status = 'seated'
        reservation.save(update_fields=['status'])
        reservation.table.status = 'occupied'
        reservation.table.save(update_fields=['status'])
        return Response(ReservationSerializer(reservation).data)
