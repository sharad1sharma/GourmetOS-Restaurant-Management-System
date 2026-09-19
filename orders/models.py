from decimal import Decimal

from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.utils import timezone

from tables.models import Table
from menu.models import MenuItem
from inventory.models import StockMovement


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),          # created, not yet confirmed by kitchen
        ('confirmed', 'Confirmed'),      # accepted, inventory deducted
        ('preparing', 'Preparing'),
        ('ready', 'Ready to Serve'),
        ('served', 'Served'),
        ('completed', 'Completed / Paid'),
        ('cancelled', 'Cancelled'),
    ]

    ORDER_TYPE_CHOICES = [
        ('dine_in', 'Dine In'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery'),
    ]

    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='orders')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='dine_in')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer_name = models.CharField(max_length=150, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} ({self.get_status_display()})"

    @property
    def total_amount(self):
        return sum((line.line_total for line in self.items.all()), Decimal('0.00'))

    # ---- Order processing -------------------------------------------------

    def check_availability(self):
        """
        Returns a list of problem strings (empty list = order can be placed).
        Checks that every line item is available and that enough inventory
        exists across the WHOLE order (multiple lines can share an ingredient).
        """
        problems = []
        required_totals = {}  # inventory_item_id -> total quantity needed

        for line in self.items.select_related('menu_item').all():
            if not line.menu_item.is_available:
                problems.append(f"'{line.menu_item.name}' is currently unavailable.")
                continue
            for recipe_line in line.menu_item.recipe_items.select_related('inventory_item').all():
                needed = recipe_line.quantity_required * line.quantity
                required_totals[recipe_line.inventory_item_id] = (
                    required_totals.get(recipe_line.inventory_item_id, Decimal('0')) + needed
                )

        from inventory.models import InventoryItem
        for inv_id, needed_qty in required_totals.items():
            inv_item = InventoryItem.objects.get(pk=inv_id)
            if inv_item.quantity_in_stock < needed_qty:
                problems.append(
                    f"Not enough '{inv_item.name}' in stock: have {inv_item.quantity_in_stock} "
                    f"{inv_item.unit}, need {needed_qty} {inv_item.unit}."
                )
        return problems

    @transaction.atomic
    def confirm(self):
        """
        Confirms the order: validates stock, then deducts inventory for every
        line item and marks the order 'confirmed'. Raises ValueError if the
        order can't be fulfilled (nothing is deducted in that case).
        """
        if self.status != 'pending':
            raise ValueError(f"Only pending orders can be confirmed (current status: {self.status}).")

        problems = self.check_availability()
        if problems:
            raise ValueError(" ".join(problems))

        for line in self.items.select_related('menu_item').all():
            for recipe_line in line.menu_item.recipe_items.select_related('inventory_item').all():
                inv_item = recipe_line.inventory_item
                needed = recipe_line.quantity_required * line.quantity
                inv_item.deduct(needed)
                StockMovement.objects.create(
                    item=inv_item,
                    change=-needed,
                    reason='order_deduction',
                    reference=f"Order #{self.pk}",
                )

        self.status = 'confirmed'
        self.save(update_fields=['status', 'updated_at'])

        if self.table:
            self.table.status = 'occupied'
            self.table.save(update_fields=['status'])

    @transaction.atomic
    def cancel(self):
        """Cancels the order. If inventory was already deducted (post-confirm), restock it."""
        if self.status in ('completed', 'cancelled'):
            raise ValueError(f"Cannot cancel an order that is already {self.status}.")

        if self.status != 'pending':
            # inventory was deducted at confirm() time -> give it back
            for line in self.items.select_related('menu_item').all():
                for recipe_line in line.menu_item.recipe_items.select_related('inventory_item').all():
                    inv_item = recipe_line.inventory_item
                    returned = recipe_line.quantity_required * line.quantity
                    inv_item.restock(returned)
                    StockMovement.objects.create(
                        item=inv_item,
                        change=returned,
                        reason='correction',
                        reference=f"Order #{self.pk} cancelled",
                    )

        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])

        if self.table and self.order_type == 'dine_in':
            self.table.status = 'available'
            self.table.save(update_fields=['status'])

    @transaction.atomic
    def mark_completed(self):
        if self.status not in ('served', 'ready', 'preparing', 'confirmed'):
            raise ValueError(f"Cannot complete an order in status '{self.status}'.")
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

        if self.table:
            self.table.status = 'cleaning'
            self.table.save(update_fields=['status'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name='order_lines')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2,
                                      help_text="Snapshot of the menu price at order time.")
    special_instructions = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('order', 'menu_item')

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)
