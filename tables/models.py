from django.db import models


class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Being Cleaned'),
    ]

    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=2)
    location = models.CharField(max_length=80, blank=True,
                                 help_text="e.g. 'Patio', 'Main Hall', 'Window'")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Table {self.number} (seats {self.capacity})"

    @property
    def is_available_now(self):
        return self.status == 'available'
