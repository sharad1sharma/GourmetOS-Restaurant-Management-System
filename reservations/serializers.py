from rest_framework import serializers
from django.utils import timezone

from .models import Reservation, DEFAULT_RESERVATION_DURATION_MINUTES
from tables.models import Table


class ReservationSerializer(serializers.ModelSerializer):
    table_number = serializers.IntegerField(source='table.number', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'table', 'table_number', 'customer_name', 'customer_phone',
            'party_size', 'reservation_time', 'duration_minutes', 'status',
            'notes', 'created_at',
        ]
        read_only_fields = ['created_at']

    def validate_reservation_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Reservation time cannot be in the past.")
        return value

    def validate(self, attrs):
        table = attrs.get('table', getattr(self.instance, 'table', None))
        party_size = attrs.get('party_size', getattr(self.instance, 'party_size', None))
        reservation_time = attrs.get('reservation_time', getattr(self.instance, 'reservation_time', None))
        duration = attrs.get('duration_minutes', getattr(self.instance, 'duration_minutes',
                                                           DEFAULT_RESERVATION_DURATION_MINUTES))

        if table and party_size and party_size > table.capacity:
            raise serializers.ValidationError(
                f"Table {table.number} only seats {table.capacity}; party size is {party_size}."
            )

        if table and reservation_time:
            clashing = Reservation.objects.filter(
                table=table, status__in=['confirmed', 'seated']
            ).exclude(pk=getattr(self.instance, 'pk', None))
            for existing in clashing:
                if existing.overlaps(reservation_time, duration):
                    raise serializers.ValidationError(
                        f"Table {table.number} is already reserved around that time "
                        f"({existing.reservation_time:%Y-%m-%d %H:%M})."
                    )
        return attrs
