from django.contrib import admin
from .models import InventoryItem, StockMovement


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_in_stock', 'unit', 'reorder_level', 'is_low_stock', 'last_restocked_at')
    list_filter = ('unit',)
    search_fields = ('name',)

    @admin.display(boolean=True)
    def is_low_stock(self, obj):
        return obj.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('item', 'change', 'reason', 'reference', 'created_at')
    list_filter = ('reason',)
    readonly_fields = ('created_at',)
