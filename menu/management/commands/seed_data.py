from decimal import Decimal

from django.core.management.base import BaseCommand

from inventory.models import InventoryItem
from menu.models import Category, MenuItem, RecipeItem
from tables.models import Table


class Command(BaseCommand):
    help = "Populate the database with sample menu items, inventory, and tables for testing."

    def handle(self, *args, **options):
        # Inventory
        tomato, _ = InventoryItem.objects.get_or_create(
            name="Tomato", defaults=dict(unit="g", quantity_in_stock=5000, reorder_level=1000, cost_per_unit=Decimal("0.05")))
        cheese, _ = InventoryItem.objects.get_or_create(
            name="Mozzarella", defaults=dict(unit="g", quantity_in_stock=3000, reorder_level=500, cost_per_unit=Decimal("0.40")))
        dough, _ = InventoryItem.objects.get_or_create(
            name="Pizza Dough", defaults=dict(unit="pcs", quantity_in_stock=40, reorder_level=10, cost_per_unit=Decimal("15.00")))
        chicken, _ = InventoryItem.objects.get_or_create(
            name="Chicken Breast", defaults=dict(unit="g", quantity_in_stock=50, reorder_level=1000, cost_per_unit=Decimal("0.30")))  # intentionally low
        rice, _ = InventoryItem.objects.get_or_create(
            name="Basmati Rice", defaults=dict(unit="kg", quantity_in_stock=25, reorder_level=5, cost_per_unit=Decimal("80.00")))

        # Menu
        pizza_cat, _ = Category.objects.get_or_create(name="Pizza")
        rice_cat, _ = Category.objects.get_or_create(name="Rice & Biryani")
        bev_cat, _ = Category.objects.get_or_create(name="Beverages")

        margherita, _ = MenuItem.objects.get_or_create(
            name="Margherita Pizza", category=pizza_cat,
            defaults=dict(price=Decimal("299.00"), is_vegetarian=True, prep_time_minutes=20))
        RecipeItem.objects.get_or_create(menu_item=margherita, inventory_item=dough, defaults=dict(quantity_required=1))
        RecipeItem.objects.get_or_create(menu_item=margherita, inventory_item=tomato, defaults=dict(quantity_required=150))
        RecipeItem.objects.get_or_create(menu_item=margherita, inventory_item=cheese, defaults=dict(quantity_required=200))

        chicken_biryani, _ = MenuItem.objects.get_or_create(
            name="Chicken Biryani", category=rice_cat,
            defaults=dict(price=Decimal("349.00"), prep_time_minutes=30))
        RecipeItem.objects.get_or_create(menu_item=chicken_biryani, inventory_item=chicken, defaults=dict(quantity_required=250))
        RecipeItem.objects.get_or_create(menu_item=chicken_biryani, inventory_item=rice, defaults=dict(quantity_required=0.3))

        MenuItem.objects.get_or_create(
            name="Masala Chai", category=bev_cat,
            defaults=dict(price=Decimal("49.00"), is_vegetarian=True, prep_time_minutes=5))

        # Tables
        for n, cap in [(1, 2), (2, 2), (3, 4), (4, 4), (5, 6), (6, 8)]:
            Table.objects.get_or_create(number=n, defaults=dict(capacity=cap))

        self.stdout.write(self.style.SUCCESS(
            "Seeded inventory, menu items (Chicken Biryani is intentionally low on stock), and 6 tables."
        ))
