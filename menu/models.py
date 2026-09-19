from django.db import models
from django.core.validators import MinValueValidator
from inventory.models import InventoryItem


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
                                  related_name='items')
    price = models.DecimalField(max_digits=8, decimal_places=2,
                                 validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True,
                                        help_text="Manually toggle to 86 an item.")
    is_vegetarian = models.BooleanField(default=False)
    image_url = models.URLField(blank=True)
    prep_time_minutes = models.PositiveIntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        """An item is sellable only if every ingredient it needs has enough stock."""
        for recipe_line in self.recipe_items.select_related('inventory_item').all():
            if recipe_line.inventory_item.quantity_in_stock < recipe_line.quantity_required:
                return False
        return True

    @property
    def is_orderable(self):
        return self.is_available and self.is_in_stock


class RecipeItem(models.Model):
    """How much of an inventory item is consumed each time one MenuItem unit is sold."""

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='recipe_items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='used_in')
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2,
                                             validators=[MinValueValidator(0.01)])

    class Meta:
        unique_together = ('menu_item', 'inventory_item')

    def __str__(self):
        return f"{self.menu_item.name} needs {self.quantity_required} {self.inventory_item.unit} of {self.inventory_item.name}"
