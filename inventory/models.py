from django.db import models
from django.core.validators import MinValueValidator


class InventoryItem(models.Model):
    """A stock-keeping unit used in the kitchen (e.g. 'Tomato', 'Cheese', 'Chicken Breast')."""

    UNIT_CHOICES = [
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('ml', 'Milliliters'),
        ('l', 'Liters'),
        ('pcs', 'Pieces'),
    ]

    name = models.CharField(max_length=120, unique=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    quantity_in_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                             validators=[MinValueValidator(0)])
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text="Stock level at/below which this item is considered low.")
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_restocked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.quantity_in_stock} {self.unit})"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    def deduct(self, amount):
        """Deduct stock. Raises ValueError if insufficient stock."""
        if amount < 0:
            raise ValueError("Deduction amount cannot be negative.")
        if self.quantity_in_stock < amount:
            raise ValueError(
                f"Insufficient stock for '{self.name}': have {self.quantity_in_stock} {self.unit}, "
                f"need {amount} {self.unit}."
            )
        self.quantity_in_stock -= amount
        self.save(update_fields=['quantity_in_stock', 'updated_at'])

    def restock(self, amount):
        if amount < 0:
            raise ValueError("Restock amount cannot be negative.")
        from django.utils import timezone
        self.quantity_in_stock += amount
        self.last_restocked_at = timezone.now()
        self.save(update_fields=['quantity_in_stock', 'last_restocked_at', 'updated_at'])


class StockMovement(models.Model):
    """Audit trail of every stock change (restock, deduction from an order, manual correction)."""

    REASON_CHOICES = [
        ('restock', 'Restock'),
        ('order_deduction', 'Order Deduction'),
        ('correction', 'Manual Correction'),
        ('waste', 'Waste / Spoilage'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    change = models.DecimalField(max_digits=10, decimal_places=2,
                                  help_text="Positive for additions, negative for deductions.")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reference = models.CharField(max_length=120, blank=True,
                                  help_text="e.g. related order number")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item.name} {self.change:+} ({self.reason})"
