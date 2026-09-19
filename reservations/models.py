from datetime import timedelta

from django.db import models
from django.core.validators import MinValueValidator
from tables.models import Table

# How long a table is considered occupied by a single reservation.
DEFAULT_RESERVATION_DURATION_MINUTES = 90


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('seated', 'Seated'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=20)
    party_size = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reservation_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=DEFAULT_RESERVATION_DURATION_MINUTES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['reservation_time']

    def __str__(self):
        return f"{self.customer_name} @ {self.table} on {self.reservation_time:%Y-%m-%d %H:%M}"

    @property
    def end_time(self):
        return self.reservation_time + timedelta(minutes=self.duration_minutes)

    def overlaps(self, other_start, other_duration_minutes):
        other_end = other_start + timedelta(minutes=other_duration_minutes)
        return self.reservation_time < other_end and other_start < self.end_time
